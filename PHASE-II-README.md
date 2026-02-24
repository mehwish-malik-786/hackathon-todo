# Phase II: Full-Stack Web Todo - Quick Start Guide

## Prerequisites

- **Python 3.12+** for backend
- **Node.js 18+** for frontend
- **Neon PostgreSQL** database (free at https://neon.tech)

---

## Backend Setup

### 1. Create Neon Database

1. Go to https://console.neon.tech
2. Create new project: `hackathon-todo`
3. Copy connection string

### 2. Configure Backend

```bash
cd backend
```

Edit `.env` file:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_db?sslmode=require
```

### 3. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access API**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

`.env.local` should have:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Frontend

```bash
npm run dev
```

**Access App**: http://localhost:3000

---

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest -v --cov=.
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Project Structure

```
hackathon-todo/
├── backend/
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings loader
│   ├── database.py             # Database connection
│   ├── models/
│   │   └── task.py             # SQLModel Task
│   ├── schemas/
│   │   └── task.py             # Pydantic schemas
│   ├── repositories/
│   │   └── task_repository.py  # CRUD operations
│   ├── routers/
│   │   └── tasks.py            # API routes
│   └── tests/
│       ├── conftest.py
│       ├── test_repository.py
│       └── test_api.py
│
└── frontend/
    ├── .env.local              # Environment variables
    ├── package.json
    ├── app/
    │   ├── layout.tsx          # Root layout
    │   ├── page.tsx            # Main page
    │   └── globals.css         # Global styles
    ├── components/
    │   ├── TaskList.tsx        # Main list component
    │   ├── TaskForm.tsx        # Add/edit form
    │   ├── TaskItem.tsx        # Single task
    │   ├── LoadingSpinner.tsx  # Loading state
    │   └── ErrorMessage.tsx    # Error display
    ├── hooks/
    │   └── useTasks.ts         # Custom hook
    ├── lib/
    │   └── api.ts              # API client
    ├── types/
    │   └── task.ts             # TypeScript types
    └── tests/
        └── components/
            ├── TaskForm.test.tsx
            └── TaskItem.test.tsx
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get task by ID |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| PATCH | `/tasks/{id}/complete` | Mark task complete |

---

## Features

✅ **Full CRUD Operations**
- Create tasks with title and optional description
- View all tasks in a list
- Update task title and/or description
- Delete tasks with confirmation
- Mark tasks as complete

✅ **Search & Filter**
- Client-side search by title or description
- Real-time filtering

✅ **Responsive UI**
- Bootstrap 5 styling
- Mobile-friendly design
- Loading states
- Error handling

✅ **Data Persistence**
- Neon PostgreSQL database
- Connection pooling
- Auto-created tables

✅ **Type Safety**
- TypeScript frontend
- Pydantic validation backend

---

## Tech Stack

### Backend
- **FastAPI** 0.109.0 - Web framework
- **SQLModel** 0.0.14 - ORM
- **Neon PostgreSQL** - Database
- **Pydantic** 2.x - Validation
- **Uvicorn** - ASGI server

### Frontend
- **Next.js** 14.1.0 - React framework
- **TypeScript** 5.x - Type safety
- **Bootstrap** 5.3 - UI styling
- **Axios** 1.x - HTTP client

---

## Troubleshooting

### Backend won't start
```bash
# Check database connection
cd backend
source venv/bin/activate
python -c "from database import engine; print(engine.connect())"
```

### Frontend can't connect to backend
```bash
# Verify API URL
cat frontend/.env.local
# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### CORS errors
- Ensure backend `.env` has correct CORS_ORIGINS
- Default: `http://localhost:3000`

### Database errors
- Verify Neon connection string is correct
- Check SSL mode is `require`
- Ensure database exists in Neon project

---

## Next Steps

1. **Deploy Backend**: Railway, Render, or Fly.io
2. **Deploy Frontend**: Vercel (recommended)
3. **Add Authentication**: JWT tokens
4. **Add Task Categories**: Tags/labels
5. **Add Due Dates**: Date picker
6. **Add Pagination**: For large task lists

---

**Happy Coding! 🚀**
