# Webhook Event Logger

A Flask-based backend service to capture GitHub webhook events (`push`, `pull_request`, `merge`) and display them in a minimal, live-updating UI using MongoDB.

---

## Features

- ✅ Logs GitHub events:
  - Push
  - Pull Request (opened)
  - Merge (closed & merged)
- ✅ Stores events in MongoDB with proper schema
- ✅ UI displays only formatted messages
- ✅ Frontend polls backend every 15 seconds
- ✅ Handles API failures gracefully
- ✅ Deployed & working on Render

---

## Project Structure

webhook-event-logger:
* app.py
* requirements.txt
* templates|-index.html
* README.md

## Technologies Used

- **Flask** – Python Web Framework
- **MongoDB Atlas** – Cloud NoSQL database
- **HTML + JavaScript** – UI for live updates
- **Render** – Free cloud deployment
- **GitHub Webhooks** – Source of triggering events

---

## 🧾 Webhook Message Format

| Action          | Message Format                                                                  |
|----------------|----------------------------------------------------------------------------------|
| **Push**        | `{author} pushed to {to_branch} on {timestamp}`                                 |
| **Pull Request**| `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` |
| **Merge**       | `{author} merged branch {from_branch} to {to_branch} on {timestamp}`            |

**Sample JSON Entry:**
```json
{
  "request_id": "abc123",
  "author": "Travis",
  "action": "MERGE",
  "from_branch": "dev",
  "to_branch": "main",
  "timestamp": "02 April 2025 - 01:45 PM UTC",
  "timestamp_utc": "2025-04-02T13:45:00Z",
  "message": "Travis merged branch dev to main on 02 April 2025 - 01:45 PM UTC"
}

# 1. Clone the repository
git clone https://github.com/Jagdishbhoi/webhook-event-logger.git
cd webhook-event-logger

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python app.py
