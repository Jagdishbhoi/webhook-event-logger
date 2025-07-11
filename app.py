from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB URI (Replace with your MongoDB Atlas URI or set via environment)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI") or "your_mongodb_uri_here"
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event", "ping")

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    try:
        if event_type == "push":
            commit = data.get("head_commit")
            if not commit:
                return jsonify({"error": "Missing head_commit"}), 400

            author = data["pusher"]["name"]
            to_branch = data["ref"].split("/")[-1]
            request_id = commit.get("id")
            timestamp_iso = commit.get("timestamp")
            timestamp = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%S%z")
            formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")

            message = f"{author} pushed to {to_branch} on {formatted_time}"
            mongo.db.events.insert_one({
                "request_id": request_id,
                "author": author,
                "action": "PUSH",
                "from_branch": "",
                "to_branch": to_branch,
                "timestamp": formatted_time,
                "message": message
            })
            return jsonify({"msg": "Push event logged"}), 200

        elif event_type == "pull_request":
            pr = data.get("pull_request")
            if not pr:
                return jsonify({"error": "Missing pull_request"}), 400

            action = data.get("action")
            from_branch = pr["head"]["ref"]
            to_branch = pr["base"]["ref"]
            request_id = str(pr["id"])

            if action == "opened":
                author = pr["user"]["login"]
                timestamp_iso = pr["created_at"]
                timestamp = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")
                message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {formatted_time}"

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "PULL_REQUEST",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "message": message
                })
                return jsonify({"msg": "Pull request logged"}), 200

            elif action == "closed" and pr.get("merged"):
                merged_by = pr.get("merged_by")
                author = merged_by["login"] if merged_by else "unknown"
                timestamp_iso = pr["merged_at"]
                timestamp = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")
                message = f"{author} merged branch {from_branch} to {to_branch} on {formatted_time}"

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "MERGE",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "message": message
                })
                return jsonify({"msg": "Merge event logged"}), 200

        return jsonify({"msg": "Event type not handled"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_events", methods=["GET"])
def get_events():
    try:
        events = mongo.db.events.find().sort("timestamp", -1)
        return jsonify([{
            "author": event["author"],
            "action": event["action"],
            "from_branch": event.get("from_branch", ""),
            "to_branch": event["to_branch"],
            "timestamp": event["timestamp"]
        } for event in events])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
    
