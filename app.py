from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)

# 🛑 Replace with your actual MongoDB URI
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
        # ✅ PUSH Event
        if event_type == "push":
            author = data["pusher"]["name"]
            to_branch = data["ref"].split("/")[-1]
            timestamp_raw = data["head_commit"]["timestamp"]
            timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%S%z")
            formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")
            request_id = data["head_commit"]["id"]

            message = f'{author} pushed to {to_branch} on {formatted_time}'

            mongo.db.events.insert_one({
                "request_id": request_id,
                "author": author,
                "action": "PUSH",
                "from_branch": "",
                "to_branch": to_branch,
                "timestamp": timestamp.isoformat(),
                "message": message
            })
            return jsonify({"msg": "Push event logged"}), 200

        # ✅ PULL REQUEST Event
        elif event_type == "pull_request":
            action = data.get("action")
            from_branch = data["pull_request"]["head"]["ref"]
            to_branch = data["pull_request"]["base"]["ref"]
            request_id = str(data["pull_request"]["id"])

            # ➕ Pull Request Opened
            if action == "opened":
                author = data["pull_request"]["user"]["login"]
                timestamp_raw = data["pull_request"]["created_at"]
                timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")
                message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {formatted_time}'

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "PULL_REQUEST",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": timestamp.isoformat(),
                    "message": message
                })
                return jsonify({"msg": "Pull Request event logged"}), 200

            # ✅ Merge Event
            elif action == "closed" and data["pull_request"].get("merged"):
                merged_by = data["pull_request"].get("merged_by")
                author = merged_by["login"] if merged_by else "unknown"
                timestamp_raw = data["pull_request"]["merged_at"]
                timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = timestamp.strftime("%d %B %Y - %I:%M %p UTC")
                message = f'{author} merged branch {from_branch} to {to_branch} on {formatted_time}'

                mongo.db.events.insert_one({
                    "request_id": request_id,
                    "author": author,
                    "action": "MERGE",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": timestamp.isoformat(),
                    "message": message
                })
                return jsonify({"msg": "Merge event logged"}), 200

        return jsonify({"msg": "Event type not handled"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fetch latest events
@app.route("/events", methods=["GET"])
def get_events():
    events = mongo.db.events.find().sort("timestamp", -1)
    output = [{"message": event["message"]} for event in events]
    return jsonify(output)
