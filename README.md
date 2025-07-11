# 📡 Webhook Event Logger

A full-stack project to receive, store, and display GitHub repository events (Push, Pull Request, Merge) using **Flask**, **MongoDB**, and a clean **HTML/CSS frontend**.

---

## Project Overview

This project captures GitHub webhook events from an **action-repo** and logs them in a **MongoDB database**. These events are then displayed on a web UI that refreshes every 15 seconds.

### Events Captured

| GitHub Action     | UI Message Format                                                  |
|-------------------|---------------------------------------------------------------------|
| Push              | `"{author} pushed to {to_branch} on {timestamp}"`                  |
| Pull Request      | `"{author} submitted a pull request from {from} to {to} on {time}"` |
| Merge (Bonus)     | `"{author} merged branch {from} to {to} on {timestamp}"`            |

---

## Technologies Used

- **Python 3 (Flask)**
- **MongoDB (Cloud via MongoDB Atlas)**
- **HTML + CSS (Frontend UI)**
- **JavaScript (Polling every 15s)**

---

## Project Structure

