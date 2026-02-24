# Task CRUD Architecture Plan

## Phase I: Console Todo App

**Feature**: Task CRUD Operations
**Spec Reference**: `specs/features/task-crud.md`
**Version**: 1.0.0
**Status**: Draft

---

## 1. Architectural Overview

### 1.1 Design Principles

- **Clean Architecture**: Domain → Infrastructure → CLI (dependency rule)
- **Single Responsibility**: Each class/module has one purpose
- **Interface-Driven**: Repository pattern for storage abstraction
- **Testability**: All logic testable without external dependencies
- **Standard Library Only**: No external packages for Phase I

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  main.py    │  │  commands.py  │  │    formatters.py    │ │
│  │  (argparse) │  │  (handlers)   │  │   (output utils)    │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │           in_memory_repository.py                        ││
│  │           (TaskRepository implementation)                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Domain Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   task.py    │  │  repository.py│  │   exceptions.py  │  │
│  │   (entity)   │  │  (interface)  │  │   (errors)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Domain Layer Design

### 2.1 Task Entity

**File**: `src/domain/task.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    """Task lifecycle status."""
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """
    Task entity representing a todo item.
    
    Attributes:
        id: Unique identifier (auto-generated, positive integer)
        title: Task title (required, 1-200 chars, non-empty)
        description: Optional description (0-1000 chars)
        status: TaskStatus enum (PENDING or COMPLETED)
        created_at: Creation timestamp (UTC, ISO 8601)
        completed_at: Completion timestamp (None if pending)
    """
    title: str
    id: int = field(default=0, init=False)
    description: Optional[str] = None
    status: TaskStatus = field(default=TaskStatus.PENDING, init=False)
    created_at: datetime = field(default_factory=datetime.utcnow, init=False)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate and normalize task data."""
        self._validate_title()
        self._normalize_description()

    def _validate_title(self):
        """Validate title constraints."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        self.title = self.title.strip()
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

    def _normalize_description(self):
        """Normalize description: empty string becomes None."""
        if self.description is not None:
            self.description = self.description.strip()
            if self.description == "":
                self.description = None
            elif len(self.description) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")

    def mark_complete(self):
        """Mark task as completed with timestamp."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
```

### 2.2 Repository Interface

**File**: `src/domain/repository.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from .task import Task


class TaskRepository(ABC):
    """
    Abstract repository interface for Task persistence.
    
    Defines the contract for task storage operations.
    Implementations can be in-memory, file-based, or database.
    """

    @abstractmethod
    def add(self, task: Task) -> Task:
        """
        Add a new task to storage.
        
        Args:
            task: Task entity to add (id will be assigned)
            
        Returns:
            Task with assigned ID
            
        Raises:
            ValueError: If task is invalid
        """
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Task]:
        """
        Retrieve task by unique ID.
        
        Args:
            id: Task unique identifier
            
        Returns:
            Task if found, None otherwise
            
        Raises:
            ValueError: If id is not a positive integer
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks in creation order.
        
        Returns:
            List of all tasks (empty list if none exist)
        """
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update an existing task.
        
        Args:
            task: Task entity with existing ID
            
        Returns:
            Updated task
            
        Raises:
            TaskNotFoundError: If task ID does not exist
            ValueError: If task is invalid
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Delete task by ID.
        
        Args:
            id: Task unique identifier
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If id is not a positive integer
        """
        pass
```

### 2.3 Custom Exceptions

**File**: `src/domain/exceptions.py`

```python
class TaskError(Exception):
    """Base exception for task-related errors."""
    pass


class TaskNotFoundError(TaskError):
    """Raised when a task with specified ID is not found."""
    
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class TaskValidationError(TaskError):
    """Raised when task validation fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
```

---

## 3. Infrastructure Layer Design

### 3.1 In-Memory Repository Implementation

**File**: `src/infrastructure/in_memory_repository.py`

```python
from typing import Dict, List, Optional
from domain.repository import TaskRepository
from domain.task import Task, TaskStatus
from domain.exceptions import TaskNotFoundError


class InMemoryTaskRepository(TaskRepository):
    """
    In-memory implementation of TaskRepository.
    
    Thread-unsafe, volatile storage for Phase I.
    Tasks are stored in a dictionary keyed by ID.
    ID generation uses auto-increment strategy.
    """

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        """Add task with auto-generated ID."""
        task.id = self._next_id
        self._next_id += 1
        self._tasks[task.id] = task
        return task

    def get_by_id(self, id: int) -> Optional[Task]:
        """Get task by ID. Returns None if not found."""
        if id <= 0:
            raise ValueError(f"Invalid task ID: {id}")
        return self._tasks.get(id)

    def get_all(self) -> List[Task]:
        """Get all tasks in creation order (by ID)."""
        return [self._tasks[id] for id in sorted(self._tasks.keys())]

    def update(self, task: Task) -> Task:
        """Update existing task."""
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)
        self._tasks[task.id] = task
        return task

    def delete(self, id: int) -> bool:
        """Delete task by ID. Returns False if not found."""
        if id <= 0:
            raise ValueError(f"Invalid task ID: {id}")
        if id in self._tasks:
            del self._tasks[id]
            return True
        return False
```

---

## 4. CLI Layer Design

### 4.1 CLI Commands Specification

**Entry Point**: `python todo.py <command> [arguments]`

| Command | Syntax | Description |
|---------|--------|-------------|
| `add` | `add <title> [--description DESC]` | Create new task |
| `list` | `list` | Display all tasks |
| `update` | `update <id> [--title TITLE] [--description DESC]` | Update task |
| `delete` | `delete <id>` | Delete task |
| `complete` | `complete <id>` | Mark task complete |
| `--help` | `--help` or `<command> --help` | Show help |
| `--version` | `--version` | Show version |

### 4.2 Command Examples

```bash
# Create task with title only
python todo.py add "Buy milk"

# Create task with title and description
python todo.py add "Buy milk" --description "From the grocery store"

# List all tasks
python todo.py list

# Update task title
python todo.py update 1 --title "Buy almond milk"

# Update task description
python todo.py update 1 --description "From the organic store"

# Update both title and description
python todo.py update 1 --title "Buy oat milk" --description "On sale"

# Delete task
python todo.py delete 1

# Mark task complete
python todo.py complete 1

# Show help
python todo.py --help
python todo.py add --help

# Show version
python todo.py --version
```

### 4.3 CLI Main Entry Point

**File**: `src/cli/main.py`

```python
import argparse
import sys
from .commands import (
    handle_add,
    handle_list,
    handle_update,
    handle_delete,
    handle_complete,
)
from infrastructure.in_memory_repository import InMemoryTaskRepository


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Task management CLI - Track your todos from the command line",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser(
        "add",
        help="Create a new task",
        description="Create a new task with a title and optional description",
    )
    add_parser.add_argument(
        "title",
        type=str,
        help="Task title (required, 1-200 characters)",
    )
    add_parser.add_argument(
        "--description",
        "-d",
        type=str,
        default=None,
        help="Task description (optional, max 1000 characters)",
    )

    # List command
    subparsers.add_parser(
        "list",
        help="Display all tasks",
        description="Show all tasks with their details",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing task",
        description="Update task title and/or description by ID",
    )
    update_parser.add_argument(
        "id",
        type=int,
        help="Task ID to update",
    )
    update_parser.add_argument(
        "--title",
        "-t",
        type=str,
        default=None,
        help="New title (optional)",
    )
    update_parser.add_argument(
        "--description",
        "-d",
        type=str,
        default=None,
        help="New description (optional)",
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
        description="Remove a task by ID",
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to delete",
    )

    # Complete command
    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark a task as completed",
        description="Mark a task as completed by ID",
    )
    complete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to complete",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    CLI entry point.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Shared repository instance (in-memory, no persistence)
    repository = InMemoryTaskRepository()

    try:
        if parsed_args.command == "add":
            handle_add(repository, parsed_args.title, parsed_args.description)
        elif parsed_args.command == "list":
            handle_list(repository)
        elif parsed_args.command == "update":
            handle_update(repository, parsed_args.id, parsed_args.title, parsed_args.description)
        elif parsed_args.command == "delete":
            handle_delete(repository, parsed_args.id)
        elif parsed_args.command == "complete":
            handle_complete(repository, parsed_args.id)
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except TaskNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### 4.4 Command Handlers

**File**: `src/cli/commands.py`

```python
from typing import Optional
from domain.repository import TaskRepository
from domain.task import Task, TaskStatus
from domain.exceptions import TaskNotFoundError
from .formatters import format_task, format_task_list


def handle_add(repository: TaskRepository, title: str, description: Optional[str] = None):
    """Handle 'add' command."""
    task = Task(title=title, description=description)
    created = repository.add(task)
    print(f"✓ Task created: {format_task(created)}")


def handle_list(repository: TaskRepository):
    """Handle 'list' command."""
    tasks = repository.get_all()
    if not tasks:
        print("No tasks found. Create one with: todo add <title>")
        return
    print(format_task_list(tasks))


def handle_update(
    repository: TaskRepository,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
):
    """Handle 'update' command."""
    existing = repository.get_by_id(task_id)
    if not existing:
        raise TaskNotFoundError(task_id)

    # Update only provided fields
    if title is not None:
        existing.title = title
    if description is not None:
        existing.description = description

    updated = repository.update(existing)
    print(f"✓ Task updated: {format_task(updated)}")


def handle_delete(repository: TaskRepository, task_id: int):
    """Handle 'delete' command."""
    if repository.delete(task_id):
        print(f"✓ Task {task_id} deleted")
    else:
        raise TaskNotFoundError(task_id)


def handle_complete(repository: TaskRepository, task_id: int):
    """Handle 'complete' command."""
    task = repository.get_by_id(task_id)
    if not task:
        raise TaskNotFoundError(task_id)

    task.mark_complete()
    repository.update(task)
    print(f"✓ Task completed: {format_task(task)}")
```

### 4.5 Output Formatters

**File**: `src/cli/formatters.py`

```python
from datetime import datetime
from typing import List
from domain.task import Task, TaskStatus


def format_task(task: Task) -> str:
    """Format single task for display."""
    status_icon = "✓" if task.status == TaskStatus.COMPLETED else "○"
    desc = f" - {task.description}" if task.description else ""
    return f"[{task.id}] {status_icon} {task.title}{desc}"


def format_task_list(tasks: List[Task]) -> str:
    """Format list of tasks for display."""
    lines = []
    for task in tasks:
        lines.append(format_task(task))
        lines.append(f"    Created: {format_datetime(task.created_at)}")
        if task.status == TaskStatus.COMPLETED and task.completed_at:
            lines.append(f"    Completed: {format_datetime(task.completed_at)}")
    return "\n".join(lines)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display (local time, readable)."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
```

---

## 5. Folder Structure

```
/home/mehwish/hackathon-todo/
├── todo.py                          # CLI entry point (runs src.cli.main)
├── src/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── task.py                  # Task entity, TaskStatus enum
│   │   ├── repository.py            # TaskRepository ABC
│   │   └── exceptions.py            # TaskError, TaskNotFoundError
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── in_memory_repository.py  # InMemoryTaskRepository
│   └── cli/
│       ├── __init__.py
│       ├── main.py                  # argparse setup, main()
│       ├── commands.py              # Command handlers
│       └── formatters.py            # Output formatting
├── tests/
│   ├── __init__.py
│   ├── test_domain/
│   │   ├── __init__.py
│   │   ├── test_task.py             # Task entity tests
│   │   └── test_exceptions.py       # Exception tests
│   ├── test_infrastructure/
│   │   ├── __init__.py
│   │   └── test_in_memory_repository.py
│   └── test_cli/
│       ├── __init__.py
│       ├── test_commands.py         # Command handler tests
│       ├── test_formatters.py       # Formatter tests
│       └── test_main.py             # CLI integration tests
├── specs/
│   ├── constitution.md
│   ├── overview.md
│   └── features/
│       └── task-crud.md
│       └── task-crud-plan.md        # This file
└── history/
    └── prompts/
```

### 5.1 Entry Point Script

**File**: `todo.py`

```python
#!/usr/bin/env python3
"""Task CLI entry point."""
import sys
from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
```

---

## 6. Test Strategy

### 6.1 Testing Framework

- **Framework**: `unittest` (standard library, per constitution)
- **Coverage Target**: ≥80% overall
- **Test Location**: `tests/` directory mirroring `src/` structure
- **Test Naming**: `test_<module>.py` with `test_<function>_<scenario>` methods

### 6.2 Test Categories

| Category | Location | Coverage Target |
|----------|----------|-----------------|
| Unit Tests - Domain | `tests/test_domain/` | 100% |
| Unit Tests - Infrastructure | `tests/test_infrastructure/` | 100% |
| Unit Tests - CLI | `tests/test_cli/` | 80%+ |

### 6.3 Test Cases Matrix

#### Domain Layer Tests

**File**: `tests/test_domain/test_task.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_task_title_only` | Valid title, no description | Task created with PENDING status |
| `test_create_task_with_description` | Valid title and description | Task created with both fields |
| `test_task_id_auto_generated` | New task | ID assigned automatically |
| `test_task_default_status_pending` | New task | status == TaskStatus.PENDING |
| `test_task_created_at_set` | New task | created_at is datetime |
| `test_task_completed_at_none` | New task | completed_at is None |
| `test_mark_complete` | Pending task | status=COMPLETED, completed_at set |
| `test_title_empty_string` | title="" | ValueError raised |
| `test_title_whitespace_only` | title="   " | ValueError raised |
| `test_title_too_long` | title > 200 chars | ValueError raised |
| `test_description_too_long` | description > 1000 chars | ValueError raised |
| `test_description_empty_becomes_none` | description="" | description is None |
| `test_to_dict` | Any task | Returns correct dict |

**File**: `tests/test_domain/test_exceptions.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_task_not_found_error` | TaskNotFoundError(5) | Message contains ID 5 |
| `test_task_validation_error` | TaskValidationError("msg") | Message stored correctly |

#### Infrastructure Layer Tests

**File**: `tests/test_infrastructure/test_in_memory_repository.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_add_assigns_id` | Add new task | Task has non-zero ID |
| `test_add_increments_id` | Add multiple tasks | Each has unique incrementing ID |
| `test_get_by_id_found` | Get existing task | Returns task |
| `test_get_by_id_not_found` | Get non-existent ID | Returns None |
| `test_get_by_id_invalid` | ID <= 0 | ValueError raised |
| `test_get_all_empty` | No tasks added | Returns [] |
| `test_get_all_order` | Multiple tasks | Returns in ID order |
| `test_update_existing` | Update valid task | Returns updated task |
| `test_update_nonexistent` | Update bad ID | TaskNotFoundError raised |
| `test_delete_existing` | Delete valid ID | Returns True, task gone |
| `test_delete_nonexistent` | Delete bad ID | Returns False |
| `test_delete_invalid_id` | ID <= 0 | ValueError raised |

#### CLI Layer Tests

**File**: `tests/test_cli/test_commands.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_handle_add_title_only` | Add with title | Task created, success message |
| `test_handle_add_with_description` | Add with both | Task created with desc |
| `test_handle_list_empty` | No tasks | "No tasks found" message |
| `test_handle_list_with_tasks` | Has tasks | Formatted list output |
| `test_handle_update_title` | Update title | Title changed |
| `test_handle_update_description` | Update desc | Description changed |
| `test_handle_update_both` | Update both | Both changed |
| `test_handle_update_not_found` | Bad ID | TaskNotFoundError |
| `test_handle_delete_existing` | Valid ID | Deleted, success message |
| `test_handle_delete_not_found` | Bad ID | TaskNotFoundError |
| `test_handle_complete_existing` | Valid ID | Status=COMPLETED |
| `test_handle_complete_not_found` | Bad ID | TaskNotFoundError |

**File**: `tests/test_cli/test_formatters.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_format_task_pending` | Pending task | Shows ○ icon |
| `test_format_task_completed` | Completed task | Shows ✓ icon |
| `test_format_task_with_description` | Has description | Description included |
| `test_format_task_list_multiple` | Multiple tasks | All formatted |
| `test_format_datetime` | Any datetime | Readable format |

**File**: `tests/test_cli/test_main.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_main_add_command` | `add "title"` | Exit 0, task added |
| `test_main_list_command` | `list` | Exit 0, output shown |
| `test_main_update_command` | `update 1 --title "x"` | Exit 0, updated |
| `test_main_delete_command` | `delete 1` | Exit 0, deleted |
| `test_main_complete_command` | `complete 1` | Exit 0, completed |
| `test_main_no_command` | No args | Exit 1, help shown |
| `test_main_invalid_command` | `foobar` | Exit 2 (argparse error) |
| `test_main_version_flag` | `--version` | Shows version |
| `test_main_help_flag` | `--help` | Shows help |

### 6.4 Test Utilities

**File**: `tests/__init__.py`

```python
import unittest
from src.domain.task import Task, TaskStatus
from src.infrastructure.in_memory_repository import InMemoryTaskRepository


def create_test_task(title="Test Task", description=None):
    """Helper to create test tasks."""
    return Task(title=title, description=description)


def create_populated_repository():
    """Helper to create repository with sample tasks."""
    repo = InMemoryTaskRepository()
    repo.add(Task(title="Task 1"))
    repo.add(Task(title="Task 2", description="Description 2"))
    return repo
```

### 6.5 Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run with verbosity
python -m unittest discover -s tests -v

# Run specific test module
python -m unittest tests.test_domain.test_task

# Run with coverage (if coverage installed)
python -m coverage run -m unittest discover -s tests
python -m coverage report --show-missing
```

---

## 7. Data Structures Summary

### 7.1 Core Data Structures

| Structure | Type | Purpose |
|-----------|------|---------|
| `Task` | dataclass | Domain entity |
| `TaskStatus` | Enum | Status values (PENDING, COMPLETED) |
| `_tasks` | Dict[int, Task] | In-memory storage |
| `_next_id` | int | ID generator counter |

### 7.2 Task Data Model

```python
Task {
    id: int                    # Auto-generated, positive integer, unique
    title: str                 # Required, 1-200 chars, trimmed
    description: str | None    # Optional, 0-1000 chars, trimmed
    status: TaskStatus         # PENDING (default) or COMPLETED
    created_at: datetime       # UTC, set on creation
    completed_at: datetime | None  # UTC, set on completion
}
```

### 7.3 ID Generation Strategy

- **Type**: Positive integers (1, 2, 3, ...)
- **Strategy**: Auto-increment counter
- **Persistence**: Reset on restart (in-memory only)
- **Deletion**: IDs NOT reused (task 3 deleted, next task = 4)

---

## 8. Error Handling Strategy

### 8.1 Error Types

| Error | When Raised | Exit Code |
|-------|-------------|-----------|
| `ValueError` | Invalid ID (<=0), validation failures | 1 |
| `TaskNotFoundError` | Task ID does not exist | 1 |
| `argparse.SystemExit` | Invalid command/args | 2 |

### 8.2 Error Messages

```
Error: Task with ID 5 not found
Error: Title cannot be empty
Error: Title cannot exceed 200 characters
Error: Description cannot exceed 1000 characters
Error: Invalid task ID: -1
```

### 8.3 Validation Layers

1. **CLI Layer**: argparse validates types (int for ID)
2. **Domain Layer**: Task entity validates title/description
3. **Repository Layer**: Validates ID is positive

---

## 9. Acceptance Criteria Mapping

| Spec Requirement | Implementation | Test |
|------------------|----------------|------|
| Create with title | `Task(title)` | `test_create_task_title_only` |
| Create with description | `Task(title, desc)` | `test_create_task_with_description` |
| Unique ID auto-assigned | `_next_id` counter | `test_add_assigns_id` |
| Default status PENDING | `TaskStatus.PENDING` | `test_task_default_status_pending` |
| Timestamp recorded | `datetime.utcnow()` | `test_task_created_at_set` |
| List all tasks | `repository.get_all()` | `test_handle_list_with_tasks` |
| Empty list message | Conditional in handler | `test_handle_list_empty` |
| Update title/desc | `handle_update()` | `test_handle_update_*` |
| Delete by ID | `handle_delete()` | `test_handle_delete_*` |
| Mark complete | `handle_complete()` | `test_handle_complete_*` |
| Invalid ID error | `TaskNotFoundError` | All `*_not_found` tests |

---

## 10. Implementation Order

### Phase 1: Domain Layer (Foundation)
1. `src/domain/exceptions.py` - Custom exceptions
2. `src/domain/task.py` - Task entity with validation
3. `src/domain/repository.py` - Repository interface

### Phase 2: Infrastructure Layer
4. `src/infrastructure/in_memory_repository.py` - In-memory implementation

### Phase 3: CLI Layer
5. `src/cli/formatters.py` - Output formatting
6. `src/cli/commands.py` - Command handlers
7. `src/cli/main.py` - CLI entry point
8. `todo.py` - Root entry point

### Phase 4: Tests (Test-First Approach)
9. `tests/test_domain/test_task.py`
10. `tests/test_domain/test_exceptions.py`
11. `tests/test_infrastructure/test_in_memory_repository.py`
12. `tests/test_cli/test_commands.py`
13. `tests/test_cli/test_formatters.py`
14. `tests/test_cli/test_main.py`

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| In-memory data loss on restart | Low (Phase I only) | Document as intentional constraint |
| ID collision in concurrent access | Low (single-user CLI) | Not applicable for Phase I |
| Title validation too strict | Medium | Adjustable constants in Task class |
| argparse complexity | Low | Simple command structure |

---

## 12. Future Considerations (Phase II+)

- **Persistence**: Replace `InMemoryTaskRepository` with `FileTaskRepository` or `DatabaseTaskRepository`
- **Dependency Injection**: Pass repository to CLI for easier testing
- **Configuration**: Externalize constants (max title length, etc.)
- **Logging**: Add logging module for debugging
- **Type Checking**: Add mypy for static type validation

---

**Version**: 1.0.0
**Created**: 2026-02-24
**Author**: AI Assistant
**Status**: Draft
**Next**: Create tasks.md with implementation checklist
