A Flask-based backend service to capture GitHub webhook events (`push`, `pull_request`, `merge`) and display them in a minimal, live-updating UI using MongoDB.

## 🚀 Technologies Used

- Python 3.x  
- Flask  
- Flask-PyMongo  
- HTML / JavaScript  
- MongoDB (local or cloud – Atlas)  
- Render (for deployment)

---

.  Features

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


## ⚙️ Setup Instructions

1. Clone the repository:

   `bash
   git clone https://github.com/Jagdishbhoi/webhook-event-logger.git
   cd webhook-event-logger

2. Install dependencies:

pip install -r requirements.txt


3. Set MongoDB URI:

Replace this line in app.py:

app.config["MONGO_URI"] = "mongodb://localhost:27017/webhookDB"

with your MongoDB Atlas URI, for example:

app.config["MONGO_URI"] = "mongodb+srv://jagdishbhoi251:<password>@cluster0.gnbiuxs.mongodb.net/webhookDB?retryWrites=true&w=majority"


4. Run the Flask application:

python app.py




---

📡 API Endpoints

Method Endpoint Description

POST /webhook Receives and logs GitHub events
GET /events Returns all stored event logs



---

👤 Author

Jagdish Raghunath Bhoi

[Github](https://github.com/Jagdishbhoi)

---

📜 License

This project is open-source and available for free use and modification.
