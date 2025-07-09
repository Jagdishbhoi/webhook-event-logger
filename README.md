---

## Technologies Used

- Python 3.x
- Flask
- Flask-PyMongo
- HTML / JavaScript
- MongoDB (local or cloud)

---

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/Jagdishbhoi/webhook-event-logger.git
cd webhook-event-logger
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure MongoDB is running locally or update the `MONGO_URI` in `app.py` to use a cloud instance.

4. Run the Flask application:

```bash
python app.py
```

---

## API Endpoints

| Method | Endpoint     | Description                    |
|--------|--------------|--------------------------------|
| POST   | /webhook     | Receives and logs GitHub events|
| GET    | /events      | Returns all stored event logs  |

---

