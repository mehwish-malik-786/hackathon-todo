# Phase II: Full-Stack Web Todo - Implementation Tasks

**Feature Name**: Task CRUD Web Application (Simplified MVP)
**Phase**: Phase II (Full-Stack Web Todo)
**Priority**: P0 (Core Feature)
**Status**: Draft
**Spec Reference**: `specs/features/phase-ii-fullstack.md`, `specs/features/phase-ii-plan.md`

---

## 1. Task Overview (Simplified)

| ID | Task | Est. Time | Priority |
|----|------|-----------|----------|
| **T001** | Setup FastAPI Backend | 1 hour | P0 |
| **T002** | Setup Neon Database | 30 min | P0 |
| **T003** | Create Task Model | 30 min | P0 |
| **T004** | Create CRUD API | 2 hours | P0 |
| **T005** | Connect Frontend | 1 hour | P0 |
| **T006** | UI Pages | 3 hours | P0 |
| **T007** | Tests | 1.5 hours | P1 |
| **Total** | **7 tasks** | **~10 hours** | |

---

## 2. Task Details

### T001: Setup FastAPI Backend

**Description**: Initialize backend project with FastAPI structure

**Files to Create**:
```
backend/
├── .env
├── .gitignore
├── requirements.txt
├── main.py
├── config.py
├── database.py
├── models/__init__.py
├── schemas/__init__.py
├── repositories/__init__.py
├── routers/__init__.py
└── tests/__init__.py
```

**Acceptance Criteria**:
- [ ] `requirements.txt` with: fastapi, uvicorn, sqlmodel, psycopg2-binary, pydantic-settings, python-dotenv, pytest, httpx
- [ ] `.env` with DATABASE_URL placeholder
- [ ] `config.py` loads environment variables
- [ ] `main.py` has FastAPI app with CORS middleware
- [ ] `database.py` has engine and session generator
- [ ] Backend runs: `uvicorn main:app --reload`

**Commands**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### T002: Setup Neon Database

**Description**: Configure Neon PostgreSQL connection

**Steps**:
1. Create Neon account at https://neon.tech
2. Create new project: `hackathon-todo`
3. Get connection string from dashboard
4. Update `backend/.env` with DATABASE_URL
5. Test connection

**Acceptance Criteria**:
- [ ] Neon project created
- [ ] DATABASE_URL in `.env` updated
- [ ] Connection pool configured in `database.py`
- [ ] Connection test successful

**Database Config**:
```python
# backend/database.py
engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
```

---

### T003: Create Task Model

**Description**: Define Task SQLModel and Pydantic schemas

**Files to Create**:
- `backend/models/task.py` - SQLModel Task
- `backend/schemas/task.py` - Pydantic schemas

**Task Model**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
```

**Schemas**:
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

**Acceptance Criteria**:
- [ ] Task model has all fields
- [ ] Schemas for create, update, response
- [ ] Validation rules match spec
- [ ] `mark_complete()` method exists

---

### T004: Create CRUD API

**Description**: Implement all 6 API endpoints

**Files to Create**:
- `backend/repositories/task_repository.py` - CRUD operations
- `backend/routers/tasks.py` - API routes

**Endpoints**:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}` | Get task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| PATCH | `/tasks/{id}/complete` | Complete task |

**Acceptance Criteria**:
- [ ] Repository: add, get_by_id, get_all, update, delete
- [ ] All 6 endpoints implemented
- [ ] Returns correct status codes (200, 201, 204, 404, 422)
- [ ] Error handling with HTTPException
- [ ] API docs at `/docs` working

**Test**:
```bash
# Test API
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Test"}'
```

---

### T005: Connect Frontend

**Description**: Set up Next.js with API client

**Files to Create**:
```
frontend/
├── .env.local
├── package.json
├── next.config.js
├── tsconfig.json
├── lib/api.ts
├── types/task.ts
└── hooks/useTasks.ts
```

**API Client**:
```typescript
// lib/api.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_URL });

export const taskApi = {
  getAll: () => api.get('/tasks'),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  complete: (id) => api.patch(`/tasks/${id}/complete`),
};
```

**Acceptance Criteria**:
- [ ] Next.js project initialized
- [ ] `.env.local` with NEXT_PUBLIC_API_URL
- [ ] API client configured
- [ ] TypeScript types defined
- [ ] useTasks hook working
- [ ] Can fetch tasks from backend

**Commands**:
```bash
cd frontend
npx create-next-app@14 . --typescript --app --no-src-dir
npm install axios
npm run dev
```

---

### T006: UI Pages

**Description**: Build all UI components

**Files to Create**:
```
frontend/app/
├── layout.tsx
├── page.tsx
├── globals.css
└── components/
    ├── TaskList.tsx
    ├── TaskForm.tsx
    ├── TaskItem.tsx
    ├── LoadingSpinner.tsx
    └── ErrorMessage.tsx
```

**Components**:
- **TaskForm**: Add/edit task with title + description
- **TaskItem**: Display single task with Complete/Edit/Delete buttons
- **TaskList**: Container with search filter
- **LoadingSpinner**: Loading state
- **ErrorMessage**: Error display

**Acceptance Criteria**:
- [ ] All components created
- [ ] Bootstrap 5 styling
- [ ] Add task works
- [ ] Update task works
- [ ] Delete task works
- [ ] Complete task works
- [ ] Search filter works (client-side)
- [ ] Loading states shown
- [ ] Error handling works
- [ ] Responsive design

**Commands**:
```bash
cd frontend
npm install bootstrap
npm run dev
# Open http://localhost:3000
```

---

### T007: Tests

**Description**: Write backend and frontend tests

**Backend Tests**:
```
backend/tests/
├── conftest.py
├── test_repository.py
└── test_api.py
```

**Frontend Tests**:
```
frontend/__tests__/components/
├── TaskForm.test.tsx
├── TaskItem.test.tsx
└── TaskList.test.tsx
```

**Acceptance Criteria**:
- [ ] Backend repository tests pass
- [ ] Backend API tests pass
- [ ] Frontend component tests pass
- [ ] Coverage: backend ≥80%, frontend ≥70%

**Commands**:
```bash
# Backend tests
cd backend
pytest -v --cov=.

# Frontend tests
cd frontend
npm test
```

---

## 3. Implementation Checklist

### Phase 1: Backend (T001-T004)
- [ ] T001: Setup FastAPI Backend
- [ ] T002: Setup Neon Database
- [ ] T003: Create Task Model
- [ ] T004: Create CRUD API

### Phase 2: Frontend (T005-T006)
- [ ] T005: Connect Frontend
- [ ] T006: UI Pages

### Phase 3: Testing (T007)
- [ ] T007: Tests

---

## 4. Definition of Done

- [ ] All 7 tasks completed
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] All CRUD operations work via UI
- [ ] Data persists in Neon database
- [ ] Tests passing
- [ ] No CORS errors
- [ ] Responsive design works

---

## 5. Quick Start

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

**Version**: 2.0.0 (Simplified)
**Created**: 2026-02-24
**Updated**: 2026-02-24
**Next**: Start with T001 - Setup FastAPI Backend
