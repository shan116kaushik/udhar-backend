# UDHAR – Backend (Python FastAPI)

> Track Money. Track Trust. — API Server

---

## 📁 Structure

```
backend/
├── main.py          ← FastAPI app entry point
├── models.py        ← SQLAlchemy DB models
├── schemas.py       ← Pydantic request/response schemas
├── crud.py          ← Database operations
├── database.py      ← DB session & engine setup
└── requirements.txt ← Python dependencies
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+

### Install & Start

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server starts at: **http://localhost:8000**  
Swagger docs at: **http://localhost:8000/docs**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/friends` | List or create friends |
| GET/PUT/DELETE | `/friends/{id}` | Get, update, or delete a friend |
| GET/POST | `/transactions` | List or create transactions |
| PUT/DELETE | `/transactions/{id}` | Update or delete a transaction |
| GET/POST | `/reminders` | List or create reminders |
| PATCH | `/reminders/{id}/complete` | Mark reminder as complete |
| GET | `/dashboard` | Summary stats |
| GET | `/export` | Export all data as JSON |

---

## 🛠 Tech Stack

| | |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (auto-created, no setup needed) |
| Language | Python 3.10+ |

---

## 🌐 Connecting from Flutter App

| Device Type | Backend URL |
|-------------|-------------|
| Android Emulator | `http://10.0.2.2:8000` |
| Physical Device (same WiFi) | `http://192.168.X.X:8000` |
| iOS Simulator | `http://localhost:8000` |

In the Flutter app: **Settings → API Server URL**
