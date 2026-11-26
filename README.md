# FinTrack | Offline Expense & Budget Tracker API

A lightweight, zero-dependency full-stack RESTful API and responsive web dashboard built with Python's standard library (`http.server`, `sqlite3`) and vanilla JavaScript. 

Designed for restricted mobile environments (iOS via Pyto/iSH) where native compilation of heavy C/Rust dependencies is restricted, this project demonstrates robust backend architecture and frontend integration without external package requirements.

---

## 🚀 Features

* **RESTful API Backend**: Fully functional `GET`, `POST`, and `DELETE` endpoints handling expense transactions.
* **Relational Data Storage**: Persistent, file-based data management using SQLite (`budget.db`).
* **Interactive Responsive UI**: Modern fintech-inspired dashboard featuring total spend calculation, category filtering, and real-time budget progress tracking with dynamic color alerts.
* **Client-Side State & Storage**: Local storage integration for custom monthly budget limits.
* **Zero-Dependency Architecture**: Built entirely using Python's native standard libraries, ensuring 100% offline compatibility across any environment.

---

## 🛠️ Tech Stack

* **Backend**: Python 3 (`http.server`, `json`, `sqlite3`, `urllib`)
* **Database**: SQLite3
* **Frontend**: HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid), Vanilla JavaScript (Fetch API)

---

## 📂 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | Serves the interactive frontend web dashboard |
| **GET** | `/expenses` | Retrieves all recorded expense transactions in JSON format |
| **POST** | `/expenses` | Creates a new expense record (JSON payload required) |
| **DELETE** | `/expenses/{id}` | Deletes a specific expense transaction by its ID |

---

## 💻 Getting Started Locally

1. Clone or copy the project repository into your workspace.
2. Run the server script using Python:
   ```bash
   python main.py
3. Open your browser and navigate to:
    (http://127.0.0.1:8000)




