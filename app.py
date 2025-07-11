@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event', 'ping')

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    try:
        # PUSH EVENT
        if event_type == "push":
            pusher = data.get("pusher")
            head_commit = data.get("head_commit")
            if not pusher or not head_commit:
                return jsonify({"error": "Missing push data"}), 400

            author = pusher["name"]
            to_branch = data["ref"].split("/")[-1]
            timestamp = head_commit["timestamp"]
            dt_utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")

            message = f"{author} pushed to {to_branch} on {formatted_time}"

            mongo.db.events.insert_one({
                "author": author,
                "event": "push",
                "from_branch": "",
                "to_branch": to_branch,
                "timestamp": formatted_time,
                "timestamp_utc": dt_utc,
                "message": message
            })

            return jsonify({"msg": "Push event logged"}), 200

        # PULL REQUEST EVENT
        elif event_type == "pull_request":
            action = data.get("action")
            pr = data.get("pull_request")
            if not pr:
                return jsonify({"error": "Missing pull_request object"}), 400

            from_branch = pr["head"]["ref"]
            to_branch = pr["base"]["ref"]
            author = pr["user"]["login"]
            request_id = str(pr["id"])

            if action == "opened":
                timestamp = pr["created_at"]
                dt_utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")

                message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {formatted_time}"

                mongo.db.events.insert_one({
                    "author": author,
                    "event": "pull_request",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "timestamp_utc": dt_utc,
                    "message": message
                })

                return jsonify({"msg": "Pull request logged"}), 200

            elif action == "closed" and pr.get("merged"):
                timestamp = pr["merged_at"]
                dt_utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                formatted_time = dt_utc.strftime("%d %B %Y - %I:%M %p UTC")
                merged_by = pr.get("merged_by")
                author = merged_by["login"] if merged_by else "unknown"

                message = f"{author} merged branch {from_branch} to {to_branch} on {formatted_time}"

                mongo.db.events.insert_one({
                    "author": author,
                    "event": "merge",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": formatted_time,
                    "timestamp_utc": dt_utc,
                    "message": message
                })

                return jsonify({"msg": "Merge event logged"}), 200

        return jsonify({"msg": "Event type not handled"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name== '__main__':
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0",port=port)
