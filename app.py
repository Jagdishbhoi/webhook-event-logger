from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Configure logging for Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Robust MongoDB connection with error handling
try:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        socketTimeoutMS=30000           # 30 second socket timeout
    )
    # Test the connection
    client.admin.command('ping')
    db = client.github_webhooks
    actions = db.actions
    logger.info(" Successfully connected to MongoDB")
except Exception as e:
    logger.error(f" MongoDB connection failed: {e}")
    raise

def parse_github_payload(data):
    """Safer payload parser with complete validation"""
    if not data:
        raise ValueError("Empty payload received")
    
    result = {
        "request_id": None,
        "author": None,
        "action": None,
        "from_branch": None,
        "to_branch": None,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    try:
        # Get author from either pusher or sender
        result["author"] = (
            data.get("pusher", {}).get("name") 
            or data.get("sender", {}).get("login")
            or "unknown"
        )

        # Handle push events
        if "commits" in data:
            result.update({
                "action": "PUSH",
                "to_branch": data.get("ref", "").split("/")[-1],
                "request_id": data.get("after")
            })

        # Handle PR events
        elif "pull_request" in data:
            pr = data["pull_request"]
            result.update({
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "request_id": str(pr["id"])
            })

            if data.get("action") == "opened":
                result["action"] = "PULL_REQUEST"
            elif data.get("action") == "closed" and pr.get("merged"):
                result["action"] = "MERGE"

    except KeyError as e:
        logger.warning(f"Missing expected key in payload: {e}")

    return result

@app.route("/webhook", methods=["POST"])
def github_webhook():
    """Webhook endpoint with complete error handling"""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        payload = request.get_json()
        entry = parse_github_payload(payload)
        
        if entry["action"]:  # Only store if we identified a valid action
            actions.insert_one(entry)
            logger.info(f"Processed {entry['action']} event from {entry['author']}")
        
        return jsonify({"status": "received"}), 200

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def dashboard():
    """Simple dashboard to view events"""
    recent_events = list(actions.find().sort("timestamp", -1).limit(10))
    return render_template("events.html", events=recent_events)

if __name__ == "__main__":
    # Render-specific configuration
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
