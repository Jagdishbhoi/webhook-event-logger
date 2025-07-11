from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/webhook_logger")
mongo = PyMongo(app)
db = mongo.db

@app.route('/')
def home():
    """Home page showing recent events"""
    try:
        events = list(db.events.find().sort("timestamp", -1).limit(10))
        return render_template('index.html', events=events)
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        return render_template('error.html'), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """GitHub webhook endpoint"""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Process different event types
        if event_type == 'push':
            event = {
                "author": data.get("pusher", {}).get("name") or "unknown",
                "action": "PUSH",
                "branch": data.get("ref", "").split("/")[-1],
                "timestamp": timestamp,
                "request_id": data.get("after")
            }
        elif event_type == 'pull_request':
            pr = data.get("pull_request", {})
            event = {
                "author": data.get("sender", {}).get("login", "unknown"),
                "action": "MERGE" if data.get("action") == "closed" and pr.get("merged") else "PULL_REQUEST",
                "from_branch": pr.get("head", {}).get("ref"),
                "to_branch": pr.get("base", {}).get("ref"),
                "timestamp": timestamp,
                "request_id": str(pr.get("id", ""))
            }
        else:
            return jsonify({"error": "Unsupported event type"}), 400

        # Insert event into MongoDB
        db.events.insert_one(event)
        logger.info(f"Processed {event['action']} event from {event['author']}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    # Use 0.0.0.0 to allow external connections
    app.run(host='0.0.0.0', port=port)
