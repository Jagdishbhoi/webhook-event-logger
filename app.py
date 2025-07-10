from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)

# Use environment variable for MongoDB URI in production!
app.config["MONGO_URI"] = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/webhookDB"
mongo = PyMongo(app)

@app.route("/")
def home():
    return "Webhook Event Logger is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event", "ping")

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    try:
        if event_type == "push":
            author = data["pusher"]["name"]
            to_branch = data["ref"].split("/")[-1]
            commit = data.get("head_commit")
            if not commit:
                return jsonify({"error": "No head_commit found in push"}), 400
            timestamp_iso = commit["timestamp"]
            dt_utc = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%S%z")
            formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")
            request_id = commit["id"]
            message = f'{author} pushed to {to_branch} on {formatted_time}'

            mongo.db.events.insert_one({
                "request_id": request_id,
                "author": author,
                "action": "PUSH",
                "from_branch": "",
                "to_branch": to_branch,
                "timestamp": formatted_time,
                "timestamp_utc": dt_utc,
                "message": message
            })
            return jsonify({"msg": "Push event logged."}), 200

        elif event_type == "pull_request":
            action = data.get("action")
            pr = data.get("pull_request")
            if not pr:
                return jsonify({"error": "No pull_request data"}), 400
            from_branch = pr["head"]["ref"]
            to_branch = pr["base"]["ref"]
            request_id = str(pr["id"])

            if action == "opened":
                author = pr["user"]["login"]
                timestamp_iso = pr["created_at"]
                dt_utc = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")
                message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {formatted_time}'

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "PULL_REQUEST",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "timestamp_utc": dt_utc,
                    "message": message
                })
                return jsonify({"msg": "Pull request logged."}), 200

            elif action == "closed" and pr.get("merged"):
                merged_by = pr.get("merged_by")
                author = merged_by["login"] if merged_by else "unknown"
                timestamp_iso = pr["merged_at"]
                dt_utc = datetime.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")
                message = f'{author} merged branch {from_branch} to {to_branch} on {formatted_time}'

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "MERGE",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "timestamp_utc": dt_utc,
                    "message": message
                })
                return jsonify({"msg": "Merge event logged."}), 200

        return jsonify({"msg": "Event type not handled"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/events", methods=["GET"])
def get_events():
    # Sort by real UTC timestamp for accuracy, newest first
    events = mongo.db.events.find().sort("timestamp_utc", -1)
    output = [{"message": event["message"]} for event in events]
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)
