
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)

# Initial (Incorrect) Mongo URI - will correct later
app.config["MONGO_URI"] = "mongodb://localhost:27017/webhookDB"
mongo = PyMongo(app)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event', 'ping')

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    if event_type == "push":
        author = data["pusher"]["name"]
        branch = data["ref"].split("/")[-1]
        timestamp = data["head_commit"]["timestamp"]
        message = f'{author} pushed to {branch} on {timestamp}'
        mongo.db.events.insert_one({
            "author": author,
            "event": "push",
            "from_branch": branch,
            "timestamp": timestamp,
            "message": message
        })
        return jsonify({"msg": "Push event logged."}), 200

    elif event_type == "pull_request":
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        timestamp = data["pull_request"]["created_at"]
        message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'
        mongo.db.events.insert_one({
            "author": author,
            "event": "pull_request",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "message": message
        })
        return jsonify({"msg": "Pull request logged."}), 200

    elif event_type == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
        author = data["pull_request"]["merged_by"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        timestamp = data["pull_request"]["merged_at"]
        message = f'{author} merged branch {from_branch} to {to_branch} on {timestamp}'
        mongo.db.events.insert_one({
            "author": author,
            "event": "merge",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "message": message
        })
        return jsonify({"msg": "Merge event logged."}), 200

    else:
        return jsonify({"msg": "Event type not handled"}), 400

@app.route('/events', methods=['GET'])
def get_events():
    events = list(mongo.db.events.find({}, {"_id": 0}))
    return jsonify(events), 200

if __name__ == '__main__':
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
