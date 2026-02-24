# Phase II: Full-Stack Web Todo - Architecture Plan

**Feature Name**: Task CRUD Web Application (Simplified MVP)
**Phase**: Phase II (Full-Stack Web Todo)
**Priority**: P0 (Core Feature)
**Status**: Draft
**Spec Reference**: `specs/features/phase-ii-fullstack.md`, `specs/constitution.md`

---

## 1. Executive Summary

Build a **simple, single-user** full-stack web application for task management.
Focus on **MVP features** for hackathon demo: persistence + REST API + responsive UI.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Users** | Single-user | No auth complexity, faster MVP |
| **Pagination** | Not implemented | Users have <100 tasks typically |
| **Search** | Client-side filter | Simple, no backend complexity |
| **Database** | Neon PostgreSQL | Managed, serverless, production-ready |
| **Backend** | FastAPI | Fast, auto OpenAPI docs, Python |
| **ORM** | SQLModel | SQLAlchemy + Pydantic unified |
| **Frontend** | Next.js 14+ | App Router, React Server Components, Vercel deploy |

---

## 2. Architecture Overview

### 2.1 Design Principles

- **Clean Architecture**: Domain → Infrastructure → API/UI layers
- **Single Responsibility**: Each module has one purpose
- **RESTful API**: Standard HTTP methods, proper status codes
- **Testability**: All logic testable without external dependencies
- **Simple First**: Avoid over-engineering for hackathon MVP

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 14+)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  TaskList   │  │  TaskForm    │  │  TaskItem / Utils       │ │
│  │  Component  │  │  Component   │  │  Components             │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│                              │                                   │
│                         (HTTP/REST)                              │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │   Routers   │  │   Services   │  │      Schemas            │ │
│  │  (routes)   │  │  (business)  │  │   (Pydantic models)     │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│                              │                                   │
│                         (SQLModel)                               │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Neon PostgreSQL (Serverless)                    ││
│  │              tasks table                                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Architecture

### 3.1 Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | FastAPI | 0.100+ | Auto docs, async support, fast |
| **ORM** | SQLModel | 0.0.14+ | SQLAlchemy + Pydantic unified |
| **Database** | Neon PostgreSQL | 15.x | Serverless, managed, production-ready |
| **Validation** | Pydantic | 2.x | Built into SQLModel |
| **Testing** | pytest | 7.x | Simple, powerful fixtures |
| **DB Driver** | psycopg2-binary | 2.9.x | PostgreSQL adapter |

### 3.2 Folder Structure

```
backend/
├── .env                          # Environment variables
├── .gitignore
├── requirements.txt              # Python dependencies
├── main.py                       # FastAPI app entry point
├── config.py                     # Configuration loader
├── database.py                   # Database connection & session
├── models/
│   ├── __init__.py
│   └── task.py                   # SQLModel Task model
├── schemas/
│   ├── __init__.py
│   └── task.py                   # Pydantic schemas (create, update, response)
├── repositories/
│   ├── __init__.py
│   └── task_repository.py        # Database CRUD operations
├── routers/
│   ├── __init__.py
│   └── tasks.py                  # API route handlers
└── tests/
    ├── __init__.py
    ├── conftest.py               # pytest fixtures
    ├── test_api.py               # API endpoint tests
    └── test_repository.py        # Repository tests
```

### 3.3 Database Schema

```sql
-- Table: tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Index for status filtering (future use)
CREATE INDEX idx_tasks_status ON tasks(status);
```

### 3.4 Domain Model

**File**: `backend/models/task.py`

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskStatus:
    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """Task domain model with database mapping."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default=TaskStatus.PENDING, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def mark_complete(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
```

### 3.5 Pydantic Schemas

**File**: `backend/schemas/task.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

### 3.6 Repository Layer

**File**: `backend/repositories/task_repository.py`

```python
from typing import List, Optional
from sqlmodel import Session, select
from models.task import Task


class TaskRepository:
    """Repository for task database operations."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> Task:
        """Add a new task."""
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, id: int) -> Optional[Task]:
        """Get task by ID."""
        return self.session.get(Task, id)

    def get_all(self) -> List[Task]:
        """Get all tasks ordered by creation date."""
        statement = select(Task).order_by(Task.created_at)
        return list(self.session.exec(statement).all())

    def update(self, task: Task) -> Task:
        """Update an existing task."""
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, id: int) -> bool:
        """Delete task by ID."""
        task = self.get_by_id(id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False
```

### 3.7 API Routes

**File**: `backend/routers/tasks.py`

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from repositories.task_repository import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_repository() -> TaskRepository:
    """Get task repository instance."""
    from database import get_session
    return TaskRepository(next(get_session()))


@router.get("", response_model=List[TaskResponse])
def list_tasks(repo: TaskRepository = None):
    """Get all tasks."""
    if repo is None:
        repo = get_repository()
    return repo.get_all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, repo: TaskRepository = None):
    """Create a new task."""
    if repo is None:
        repo = get_repository()
    task = Task(**task_data.model_dump())
    return repo.add(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, repo: TaskRepository = None):
    """Get task by ID."""
    if repo is None:
        repo = get_repository()
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, repo: TaskRepository = None):
    """Update an existing task."""
    if repo is None:
        repo = get_repository()
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    return repo.update(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, repo: TaskRepository = None):
    """Delete a task."""
    if repo is None:
        repo = get_repository()
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    repo.delete(task_id)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, repo: TaskRepository = None):
    """Mark task as completed."""
    if repo is None:
        repo = get_repository()
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    task.mark_complete()
    return repo.update(task)
```

### 3.8 Main Application

**File**: `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks
from database import create_db_tables

app = FastAPI(
    title="Hackathon TODO API",
    description="Simple task management API for hackathon demo",
    version="1.0.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_db_tables()


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Hackathon TODO API", "docs": "/docs"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### 3.9 Database Configuration

**File**: `backend/database.py`

```python
from sqlmodel import SQLModel, create_engine, Session
from config import get_settings

settings = get_settings()

# Neon PostgreSQL connection with connection pooling
engine = create_engine(
    settings.database_url,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
)


def create_db_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session generator."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
```

**File**: `backend/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "sqlite:///./tasks.db"
    api_url: str = "http://localhost:8000"
    cors_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()
```

**File**: `backend/.env`

```bash
# Neon PostgreSQL connection string
# Get from: https://console.neon.tech/app/projects
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_db?sslmode=require

API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

---

## 4. Frontend Architecture

### 4.1 Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | Next.js | 14.x | App Router, RSC, Vercel deploy |
| **Language** | TypeScript | 5.x | Type safety, better DX |
| **Styling** | Bootstrap 5 | 5.x | Quick responsive UI |
| **HTTP Client** | Axios | 1.x | Simple API calls |
| **State** | React useState/useEffect | Built-in | No extra deps for MVP |
| **Deploy** | Vercel | - | Serverless, auto CI/CD |

### 4.2 Folder Structure

```
frontend/
├── .env.local                    # Environment variables
├── .gitignore
├── package.json                  # Node dependencies
├── next.config.js                # Next.js configuration
├── app/
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Task list page
│   ├── globals.css               # Global styles
│   └── components/
│       ├── TaskList.tsx          # Task list container
│       ├── TaskForm.tsx          # Add/edit task form
│       ├── TaskItem.tsx          # Single task display
│       ├── LoadingSpinner.tsx    # Loading indicator
│       └── ErrorMessage.tsx      # Error display
├── lib/
│   └── api.ts                    # Axios API client
├── types/
│   └── task.ts                   # TypeScript types
├── hooks/
│   └── useTasks.ts               # Custom hook for tasks
└── __tests__/
    └── components/
        ├── TaskList.test.tsx
        ├── TaskForm.test.tsx
        └── TaskItem.test.tsx
```

### 4.3 API Client

**File**: `frontend/lib/api.ts`

```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
}

export const taskApi = {
  getAll: () => api.get<Task[]>('/tasks'),
  getById: (id: number) => api.get<Task>(`/tasks/${id}`),
  create: (data: TaskCreate) => api.post<Task>('/tasks', data),
  update: (id: number, data: TaskUpdate) => api.put<Task>(`/tasks/${id}`, data),
  delete: (id: number) => api.delete(`/tasks/${id}`),
  complete: (id: number) => api.patch<Task>(`/tasks/${id}/complete`),
};

export default api;
```

### 4.4 Custom Hook

**File**: `frontend/hooks/useTasks.ts`

```typescript
import { useState, useEffect, useCallback } from 'react';
import { taskApi, Task, TaskCreate } from '../lib/api';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await taskApi.getAll();
      setTasks(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  const addTask = useCallback(async (title: string, description?: string) => {
    const data: TaskCreate = { title, description };
    const response = await taskApi.create(data);
    setTasks(prev => [...prev, response.data]);
    return response.data;
  }, []);

  const updateTask = useCallback(async (id: number, updates: { title?: string; description?: string }) => {
    const response = await taskApi.update(id, updates);
    setTasks(prev => prev.map(t => t.id === id ? response.data : t));
    return response.data;
  }, []);

  const deleteTask = useCallback(async (id: number) => {
    await taskApi.delete(id);
    setTasks(prev => prev.filter(t => t.id !== id));
  }, []);

  const completeTask = useCallback(async (id: number) => {
    const response = await taskApi.complete(id);
    setTasks(prev => prev.map(t => t.id === id ? response.data : t));
    return response.data;
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    loading,
    error,
    addTask,
    updateTask,
    deleteTask,
    completeTask,
    refresh: fetchTasks,
  };
}
```

### 4.5 Components

**File**: `frontend/src/components/TaskForm.jsx`

```jsx
import React, { useState } from 'react';

function TaskForm({ onAdd, editingTask, onUpdate, onCancelEdit }) {
  const [title, setTitle] = useState(editingTask?.title || '');
  const [description, setDescription] = useState(editingTask?.description || '');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    if (editingTask) {
      await onUpdate(editingTask.id, { title, description });
      setTitle('');
      setDescription('');
      onCancelEdit();
    } else {
      await onAdd(title, description);
      setTitle('');
      setDescription('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div className="mb-2">
        <textarea
          className="form-control"
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows="2"
        />
      </div>
      <div className="d-flex gap-2">
        <button type="submit" className="btn btn-primary">
          {editingTask ? 'Update' : 'Add Task'}
        </button>
        {editingTask && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancelEdit}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default TaskForm;
```

**File**: `frontend/src/components/TaskItem.jsx`

```jsx
import React from 'react';

function TaskItem({ task, onEdit, onDelete, onComplete }) {
  const isCompleted = task.status === 'completed';

  return (
    <div className={`card mb-2 ${isCompleted ? 'bg-light' : ''}`}>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div className="flex-grow-1">
            <h5 className={isCompleted ? 'text-decoration-line-through' : ''}>
              {isCompleted ? '✓' : '○'} {task.title}
            </h5>
            {task.description && (
              <p className="text-muted mb-0">{task.description}</p>
            )}
            <small className="text-muted">
              Created: {new Date(task.created_at).toLocaleString()}
            </small>
            {task.completed_at && (
              <div>
                <small className="text-success">
                  Completed: {new Date(task.completed_at).toLocaleString()}
                </small>
              </div>
            )}
          </div>
          <div className="btn-group">
            {!isCompleted && (
              <button
                className="btn btn-sm btn-success"
                onClick={() => onComplete(task.id)}
              >
                Complete
              </button>
            )}
            <button
              className="btn btn-sm btn-primary"
              onClick={() => onEdit(task)}
            >
              Edit
            </button>
            <button
              className="btn btn-sm btn-danger"
              onClick={() => onDelete(task.id)}
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TaskItem;
```

**File**: `frontend/src/components/TaskList.jsx`

```jsx
import React, { useState, useMemo } from 'react';
import TaskForm from './TaskForm';
import TaskItem from './TaskItem';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

function TaskList() {
  const {
    tasks,
    loading,
    error,
    addTask,
    updateTask,
    deleteTask,
    completeTask,
  } = useTasks();

  const [editingTask, setEditingTask] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Client-side search filter
  const filteredTasks = useMemo(() => {
    if (!searchQuery.trim()) return tasks;
    const query = searchQuery.toLowerCase();
    return tasks.filter(
      task =>
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query))
    );
  }, [tasks, searchQuery]);

  const handleEdit = (task) => setEditingTask(task);
  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Hackathon TODO</h1>

      <TaskForm
        onAdd={addTask}
        editingTask={editingTask}
        onUpdate={updateTask}
        onCancelEdit={handleCancelEdit}
      />

      <div className="mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="task-list">
        {filteredTasks.length === 0 ? (
          <p className="text-muted">
            {searchQuery ? 'No tasks match your search.' : 'No tasks found. Create one above!'}
          </p>
        ) : (
          filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onEdit={handleEdit}
              onDelete={deleteTask}
              onComplete={completeTask}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default TaskList;
```

**File**: `frontend/app/page.tsx`

```tsx
'use client';

import TaskList from './components/TaskList';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function Home() {
  return (
    <main className="container mt-4">
      <TaskList />
    </main>
  );
}
```

**File**: `frontend/app/layout.tsx`

```tsx
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Hackathon TODO',
  description: 'Simple task management app',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 4.6 Environment Configuration

**File**: `frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**File**: `frontend/package.json`

```json
{
  "name": "hackathon-todo-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "bootstrap": "^5.3.0",
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

**File**: `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
```

**File**: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## 5. API Specification

### 5.1 Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/tasks` | List all tasks | - | `Task[]` |
| `POST` | `/tasks` | Create task | `TaskCreate` | `Task` |
| `GET` | `/tasks/{id}` | Get task | - | `Task` |
| `PUT` | `/tasks/{id}` | Update task | `TaskUpdate` | `Task` |
| `DELETE` | `/tasks/{id}` | Delete task | - | `204` |
| `PATCH` | `/tasks/{id}/complete` | Complete task | - | `Task` |

### 5.2 Request/Response Examples

**POST /tasks** - Create task
```json
// Request
{
  "title": "Buy milk",
  "description": "From the grocery store"
}

// Response (201 Created)
{
  "id": 1,
  "title": "Buy milk",
  "description": "From the grocery store",
  "status": "pending",
  "created_at": "2026-02-24T10:30:00Z",
  "completed_at": null
}
```

**PATCH /tasks/1/complete** - Mark complete
```json
// Response (200 OK)
{
  "id": 1,
  "title": "Buy milk",
  "description": "From the grocery store",
  "status": "completed",
  "created_at": "2026-02-24T10:30:00Z",
  "completed_at": "2026-02-24T12:00:00Z"
}
```

### 5.3 Error Responses

**404 Not Found**
```json
{
  "detail": "Task with ID 999 not found"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

## 6. Testing Strategy

### 6.1 Backend Tests

**File**: `backend/tests/test_repository.py`

```python
import pytest
from sqlmodel import Session, create_engine
from models.task import Task
from repositories.task_repository import TaskRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///./test_tasks.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def repo(session):
    return TaskRepository(session)


def test_add_task(repo):
    task = Task(title="Test Task")
    result = repo.add(task)
    assert result.id is not None
    assert result.title == "Test Task"


def test_get_all(repo):
    repo.add(Task(title="Task 1"))
    repo.add(Task(title="Task 2"))
    tasks = repo.get_all()
    assert len(tasks) == 2


def test_complete_task(repo):
    task = repo.add(Task(title="Test"))
    task.mark_complete()
    repo.update(task)
    assert task.status == "completed"
```

**File**: `backend/tests/test_api.py`

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Test", "description": "Desc"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert data["status"] == "pending"


def test_complete_task():
    # Create first
    create = client.post("/tasks", json={"title": "Test"})
    task_id = create.json()["id"]

    # Complete
    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_task():
    create = client.post("/tasks", json={"title": "Test"})
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    get = client.get(f"/tasks/{task_id}")
    assert get.status_code == 404
```

### 6.2 Frontend Tests

**File**: `frontend/__tests__/components/TaskForm.test.jsx`

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import TaskForm from '../../components/TaskForm';

describe('TaskForm', () => {
  test('calls onAdd when form submitted', () => {
    const onAdd = vi.fn();
    render(<TaskForm onAdd={onAdd} />);

    fireEvent.change(screen.getByPlaceholderText('Task title'), {
      target: { value: 'Test Task' },
    });
    fireEvent.click(screen.getByText('Add Task'));

    expect(onAdd).toHaveBeenCalledWith('Test Task', '');
  });
});
```

---

## 7. Running the Application

### 7.1 Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

**File**: `backend/requirements.txt`

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.4
httpx==0.26.0
```

### 7.2 Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access app
# http://localhost:3000

# Build for production
npm run build

# Start production server
npm start
```

---

## 8. Acceptance Criteria

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
- [ ] SQLite database persistence works
- [ ] Client-side search filter works

### Won't Have (Phase II - Simplified)

- [ ] User authentication
- [ ] Multi-user support
- [ ] Pagination
- [ ] Server-side filtering/sorting
- [ ] Task priorities
- [ ] Due dates
- [ ] Task categories/tags
- [ ] Real-time updates

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| API endpoints functional | 5/5 |
| UI components working | All CRUD operations |
| Test coverage (backend) | ≥80% |
| Test coverage (frontend) | ≥70% |
| Performance (p95) | < 200ms |
| Zero critical bugs | Pass |

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SQLite file locking | Medium | Use proper session management |
| CORS configuration | Medium | Explicit origins in backend |
| State management complexity | Low | Use custom hooks, keep simple |
| API contract changes | Low | Version API from start (`/api/v1`) |

---

## 11. References

- Project Constitution: `specs/constitution.md`
- Project Overview: `specs/overview.md`
- Phase I Spec: `specs/features/task-crud.md`
- Phase I Plan: `specs/features/task-crud-plan.md`
- Phase II Spec: `specs/features/phase-ii-fullstack.md`
- Backend .env: `backend/.env`
- Frontend .env.local: `frontend/.env.local`

---

**Version**: 1.0.0
**Created**: 2026-02-24
**Author**: AI Assistant
**Status**: Draft
**Next**: Create implementation tasks (`specs/features/phase-ii-tasks.md`)
