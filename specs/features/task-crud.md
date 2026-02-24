# Task CRUD Feature Specification

## Feature Overview

**Feature Name**: Task CRUD Operations  
**Phase**: Phase I (Console Todo App)  
**Priority**: P0 (Core Feature)  
**Status**: Pending

---

## Requirements

### Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-001 | Add Task | User can create a new task with title and description |
| FR-002 | Delete Task | User can delete an existing task by ID |
| FR-003 | Update Task | User can update task title and/or description |
| FR-004 | View Tasks | User can list all tasks |
| FR-005 | Mark Complete | User can mark a task as completed |

### Non-Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-001 | In-Memory Storage | Tasks stored in memory (no persistence required) |
| NFR-002 | Python CLI | All operations via Python command-line interface |
| NFR-003 | Modular Structure | Clean separation: domain, repository, CLI layers |
| NFR-004 | Unit Tests | 80%+ code coverage with comprehensive unit tests |

---

## User Stories

### US-001: Create Task
```
As a user,
I want to create a task with a title and description,
So that I can track things I need to do.
```

**Acceptance Criteria**:
- [ ] User can create task with title (required)
- [ ] User can create task with description (optional)
- [ ] Task is assigned a unique ID automatically
- [ ] Task status defaults to "pending"
- [ ] Task creation timestamp is recorded
- [ ] Success message displays created task details

---

### US-002: List Tasks
```
As a user,
I want to view all my tasks,
So that I can see what I need to do.
```

**Acceptance Criteria**:
- [ ] User can list all tasks
- [ ] Each task displays: ID, title, description, status, created date
- [ ] Empty list shows appropriate message when no tasks exist
- [ ] Tasks are displayed in creation order

---

### US-003: Update Task
```
As a user,
I want to update an existing task,
So that I can correct or modify task details.
```

**Acceptance Criteria**:
- [ ] User can update task title by ID
- [ ] User can update task description by ID
- [ ] User can update both title and description
- [ ] Invalid task ID shows error message
- [ ] Success message confirms update

---

### US-004: Delete Task
```
As a user,
I want to delete a task,
So that I can remove tasks I no longer need.
```

**Acceptance Criteria**:
- [ ] User can delete task by ID
- [ ] Invalid task ID shows error message
- [ ] Deleted task is removed from memory
- [ ] Success message confirms deletion

---

### US-005: Mark Complete
```
As a user,
I want to mark a task as completed,
So that I can track my progress.
```

**Acceptance Criteria**:
- [ ] User can mark task as completed by ID
- [ ] Task status changes from "pending" to "completed"
- [ ] Completion timestamp is recorded
- [ ] Invalid task ID shows error message
- [ ] Success message confirms completion

---

## Technical Specifications

### Domain Model

```python
class Task:
    id: int
    title: str
    description: str | None
    status: TaskStatus  # PENDING | COMPLETED
    created_at: datetime
    completed_at: datetime | None
```

### Repository Interface

```python
class TaskRepository:
    def add(self, task: Task) -> Task
    def get_by_id(self, id: int) -> Task | None
    def get_all(self) -> list[Task]
    def update(self, task: Task) -> Task
    def delete(self, id: int) -> bool
```

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create new task | `python todo.py add "Buy milk" --description "From store"` |
| `list` | View all tasks | `python todo.py list` |
| `update` | Update task | `python todo.py update 1 --title "New title"` |
| `delete` | Delete task | `python todo.py delete 1` |
| `complete` | Mark complete | `python todo.py complete 1` |

---

## Constraints

1. **In-Memory Storage Only**: No file or database persistence
2. **Python CLI**: Command-line interface using argparse or typer
3. **Clean Architecture**: Separate domain, repository, and CLI layers
4. **Unit Tests Required**: All functions must have unit tests
5. **Standard Library Only**: No external dependencies for Phase I

---

## Acceptance Criteria Summary

### Must Have (P0)
- [ ] User can create task with title (required) and description (optional)
- [ ] User can list all tasks with full details
- [ ] User can update task title and/or description by ID
- [ ] User can delete task by ID
- [ ] User can mark task as complete by ID
- [ ] All operations provide clear success/error messages
- [ ] Invalid task IDs handled gracefully

### Won't Have (Phase I)
- [ ] Data persistence to file/DB
- [ ] Task filtering/sorting
- [ ] Task priorities
- [ ] Due dates

---

## Testing Requirements

### Unit Tests

| Test Suite | Coverage |
|------------|----------|
| Task entity tests | 100% |
| TaskRepository tests | 100% |
| CLI command tests | 80%+ |

### Test Cases

**Add Task**:
- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] Verify unique ID assignment
- [ ] Verify default status is pending

**List Tasks**:
- [ ] List empty repository
- [ ] List single task
- [ ] List multiple tasks in order

**Update Task**:
- [ ] Update title only
- [ ] Update description only
- [ ] Update both title and description
- [ ] Update non-existent task (error)

**Delete Task**:
- [ ] Delete existing task
- [ ] Delete non-existent task (error)

**Mark Complete**:
- [ ] Mark pending task complete
- [ ] Mark non-existent task (error)

---

## Implementation Notes

### Module Structure
```
phase-1-cli/
├── domain/
│   ├── task.py          # Task entity
│   ├── repository.py    # TaskRepository interface
│   └── exceptions.py    # Custom exceptions
├── infrastructure/
│   └── in_memory_repository.py  # In-memory implementation
├── cli/
│   ├── main.py          # CLI entry point
│   ├── commands.py      # Command handlers
│   └── formatters.py    # Output formatting
└── tests/
    ├── test_domain.py
    ├── test_repository.py
    └── test_cli.py
```

### Dependencies (Phase I)
- Python 3.13+
- Standard library only (argparse, dataclasses, datetime)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Unit Test Coverage | ≥80% |
| All Acceptance Criteria | Pass |
| CLI Commands | All functional |
| Error Handling | Graceful |

---

## References

- Project Constitution: `specs/constitution.md`
- Project Overview: `specs/overview.md`

---

**Version**: 1.0.0  
**Created**: 2026-02-24  
**Author**: AI Assistant  
**Status**: Draft
