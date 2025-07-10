from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(name)

# MongoDB setup (Render will provide MONGO_URI)
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client.webhook_logger
events = db.events

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    data = request.json

    # Push event
    if event == 'push':
        events.insert_one({
            'author': data['pusher']['name'],
            'action': 'PUSH',
            'branch': data['ref'].split('/')[-1],
            'timestamp': datetime.strptime(
                data['head_commit']['timestamp'], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %B %Y - %I:%M %p UTC")
        })

    # Pull Request event
    elif event == 'pull_request' and data['action'] == 'opened':
        events.insert_one({
            'author': data['sender']['login'],
            'action': 'PULL_REQUEST',
            'from_branch': data['pull_request']['head']['ref'],
            'to_branch': data['pull_request']['base']['ref'],
            'timestamp': datetime.strptime(
                data['pull_request']['created_at'], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %B %Y - %I:%M %p UTC")
        })

    # Merge event
    elif event == 'pull_request' and data['action'] == 'closed' and data['pull_request']['merged']:
        events.insert_one({
            'author': data['sender']['login'],
            'action': 'MERGE',
            'from_branch': data['pull_request']['head']['ref'],
            'to_branch': data['pull_request']['base']['ref'],
            'timestamp': datetime.strptime(
                data['pull_request']['merged_at'], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %B %Y - %I:%M %p UTC")
        })

    return jsonify({'status': 'success'}), 200

@app.route('/get_events')
def get_events():
    return jsonify(list(events.find().sort('timestamp', -1).limit(10)))

if name == 'main':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
