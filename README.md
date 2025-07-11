A Flask-based backend service to capture GitHub webhook events (`push`, `pull_request`, `merge`) and display them in a minimal, live-updating UI using MongoDB.

---

##  Features

- ✅ Logs GitHub events:
  - Push
  - Pull Request (opened)
  - Merge (closed & merged)
- ✅ Stores events in MongoDB with required schema
- ✅ Displays clean, formatted messages on frontend
- ✅ UI auto-refreshes every 15 seconds
- ✅ Graceful error handling in frontend
- ✅ Fully deployed and working on Render

---

##  Project Structure

webhook-event-logger/
│
├── app.py
├── requirements.txt
│
├── templates/
└── index.html


yaml
Copy
Edit

---

##  Technologies Used

- **Flask** – Web framework (Python)
- **MongoDB Atlas** – Cloud NoSQL database
- **HTML + JavaScript** – Frontend UI
- **Render** – For cloud deployment
- **GitHub Webhooks** – For triggering real-time events

---

## 🧾 Webhook Event Format

| Action         | Format                                                                 |
|----------------|------------------------------------------------------------------------|
| **Push**        | `{author} pushed to {to_branch} on {timestamp}`                        |
| **Pull Request**| `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` |
| **Merge**       | `{author} merged branch {from_branch} to {to_branch} on {timestamp}`   |

###  MongoDB Schema Example:

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
 How to Run Locally
bash
Copy
Edit
# 1. Clone the repository
git clone https://github.com/Jagdishbhoi/webhook-event-logger.git
cd webhook-event-logger

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # For Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask server
python app.py
