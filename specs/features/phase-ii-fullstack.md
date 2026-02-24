# Phase II: Full-Stack Web Todo - Feature Specification

**Feature Name**: Task CRUD Web Application  
**Phase**: Phase II (Full-Stack Web Todo)  
**Priority**: P0 (Core Feature)  
**Status**: Draft  
**Spec Reference**: `specs/constitution.md`, `specs/overview.md`

---

## Feature Overview

Build a full-stack web application for task management with RESTful API backend and responsive web UI.

### User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-001 | As a user, I want to add a task via web UI | P0 |
| US-002 | As a user, I want to update a task | P0 |
| US-003 | As a user, I want to delete a task | P0 |
| US-004 | As a user, I want to mark a task complete | P0 |
| US-005 | As a user, I want to view all tasks | P0 |

---

## Functional Requirements

### Web UI Features

| ID | Feature | Description |
|----|---------|-------------|
| FR-UI-001 | Add Task | Form to create task with title and description |
| FR-UI-002 | Update Task | Edit task title and/or description |
| FR-UI-003 | Delete Task | Remove task with confirmation |
| FR-UI-004 | Complete Task | Toggle task completion status |
| FR-UI-005 | View Tasks | Display all tasks in a list/table |
| FR-UI-006 | Loading States | Show loading indicators during API calls |
| FR-UI-007 | Error Handling | Display user-friendly error messages |

### API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/tasks` | Get all tasks | None | `List[Task]` |
| `POST` | `/tasks` | Create new task | `{title, description}` | `Task` |
| `PUT` | `/tasks/{id}` | Update task | `{title?, description?}` | `Task` |
| `DELETE` | `/tasks/{id}` | Delete task | None | `204 No Content` |
| `PATCH` | `/tasks/{id}/complete` | Mark task complete | None | `Task` |

---

## Technical Specifications

### Backend Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT (future phase)
- **Environment**: `.env` for secrets

### Frontend Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query / SWR
- **HTTP Client**: Fetch API / Axios

### Database Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Domain Model

```python
# Backend (SQLModel)
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

# Frontend (TypeScript)
interface Task {
    id: number;
    title: string;
    description: string | null;
    status: 'pending' | 'completed';
    createdAt: string;
    completedAt: string | null;
}
```

---

## API Response Formats

### Success Responses

**GET /tasks** - List all tasks
```json
[
  {
    "id": 1,
    "title": "Buy milk",
    "description": "From the grocery store",
    "status": "pending",
    "createdAt": "2026-02-24T10:30:00Z",
    "completedAt": null
  }
]
```

**POST /tasks** - Create task
```json
{
  "id": 2,
  "title": "New task",
  "description": "Task description",
  "status": "pending",
  "createdAt": "2026-02-24T11:00:00Z",
  "completedAt": null
}
```

**PUT /tasks/{id}** - Update task
```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "status": "pending",
  "createdAt": "2026-02-24T10:30:00Z",
  "completedAt": null
}
```

**DELETE /tasks/{id}** - Delete task
```
Status: 204 No Content
```

**PATCH /tasks/{id}/complete** - Mark complete
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "From the grocery store",
  "status": "completed",
  "createdAt": "2026-02-24T10:30:00Z",
  "completedAt": "2026-02-24T12:00:00Z"
}
```

### Error Responses

**404 Not Found**
```json
{
  "detail": "Task with ID 999 not found"
}
```

**400 Bad Request**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Performance | API response < 200ms (p95) |
| NFR-002 | Availability | 99% uptime |
| NFR-003 | Security | CORS configured, SQL injection prevention |
| NFR-004 | Scalability | Support 1000 concurrent users |
| NFR-005 | Code Quality | 80%+ test coverage |
| NFR-006 | Documentation | OpenAPI/Swagger docs |

---

## Environment Configuration

### Backend (.env)

```bash
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Folder Structure

### Backend

```
backend/
├── .env
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration loader
├── database.py             # Database connection
├── models/
│   └── task.py             # SQLModel Task model
├── schemas/
│   └── task.py             # Pydantic schemas
├── repositories/
│   └── task_repository.py  # Database operations
├── routers/
│   └── tasks.py            # API routes
├── services/
│   └── task_service.py     # Business logic
└── tests/
    ├── test_api.py
    └── test_repository.py
```

### Frontend

```
frontend/
├── .env.local
├── app/
│   ├── layout.tsx
│   ├── page.tsx            # Task list page
│   └── components/
│       ├── TaskList.tsx
│       ├── TaskForm.tsx
│       ├── TaskItem.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   └── api.ts              # API client
├── types/
│   └── task.ts             # TypeScript types
└── __tests__/
    └── components/
```

---

## Acceptance Criteria

### Must Have (P0)

- [ ] User can create task via web form
- [ ] User can view all tasks in a list
- [ ] User can update task title/description
- [ ] User can delete task (with confirmation)
- [ ] User can mark task as complete
- [ ] API endpoints return correct responses
- [ ] Error messages displayed for failures
- [ ] Loading states shown during operations
- [ ] Responsive UI (mobile + desktop)
- [ ] Database persistence works

### Won't Have (Phase II)

- [ ] User authentication
- [ ] Task filtering/sorting
- [ ] Task priorities
- [ ] Due dates
- [ ] Task categories/tags
- [ ] Real-time updates

---

## Testing Requirements

### Backend Tests

| Test Suite | Coverage |
|------------|----------|
| Repository tests | 100% |
| API endpoint tests | 90%+ |
| Service layer tests | 80%+ |

### Frontend Tests

| Test Suite | Coverage |
|------------|----------|
| Component tests | 80%+ |
| Integration tests | 70%+ |
| E2E tests | Critical paths |

---

## Implementation Tasks

### Backend (T001-T010)

| ID | Task | Est. Effort |
|----|------|-------------|
| T001 | Set up FastAPI project structure | 30 min |
| T002 | Configure SQLModel and database connection | 30 min |
| T003 | Create Task model | 15 min |
| T004 | Implement TaskRepository | 45 min |
| T005 | Create Pydantic schemas | 20 min |
| T006 | Implement GET /tasks endpoint | 30 min |
| T007 | Implement POST /tasks endpoint | 30 min |
| T008 | Implement PUT /tasks/{id} endpoint | 30 min |
| T009 | Implement DELETE /tasks/{id} endpoint | 20 min |
| T010 | Implement PATCH /tasks/{id}/complete | 20 min |

### Frontend (T011-T020)

| ID | Task | Est. Effort |
|----|------|-------------|
| T011 | Set up Next.js project | 30 min |
| T012 | Configure Tailwind CSS | 20 min |
| T013 | Create API client | 30 min |
| T014 | Define TypeScript types | 15 min |
| T015 | Build TaskList component | 45 min |
| T016 | Build TaskForm component | 45 min |
| T017 | Build TaskItem component | 30 min |
| T018 | Implement create task flow | 30 min |
| T019 | Implement update task flow | 30 min |
| T020 | Implement delete/complete flows | 30 min |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| API endpoints functional | 5/5 |
| UI components working | All CRUD operations |
| Test coverage | ≥80% |
| Performance (p95) | < 200ms |
| Zero critical bugs | Pass |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection issues | High | Connection pooling, retry logic |
| CORS configuration | Medium | Explicit origins in backend |
| State management complexity | Low | Use React Query for caching |
| API contract changes | Medium | Version API from start |

---

## References

- Project Constitution: `specs/constitution.md`
- Project Overview: `specs/overview.md`
- Phase I Spec: `specs/features/task-crud.md`
- Backend .env: `backend/.env`
- Frontend .env.local: `frontend/.env.local`

---

**Version**: 1.0.0  
**Created**: 2026-02-24  
**Author**: AI Assistant  
**Status**: Draft  
**Next**: Create architecture plan (`specs/features/phase-ii-plan.md`)
