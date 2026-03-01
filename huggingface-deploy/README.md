# Hugging Face Space for Hackathon TODO API

A full-stack task management application built with FastAPI and Next.js.

## 🚀 Features

- Create, Read, Update, Delete tasks
- Mark tasks as complete
- Search and filter tasks
- Responsive UI with Bootstrap
- PostgreSQL database (Neon)

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLModel, PostgreSQL
- **Frontend:** Next.js, React, TypeScript, Bootstrap
- **Database:** Neon PostgreSQL

## 📦 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get task by ID |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| PATCH | `/tasks/{id}/complete` | Mark complete |

## 🧪 Test Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860

# Frontend
cd frontend
npm install
npm run dev
```

## 📄 License

MIT