---
title: Hackathon Todo Backend
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
# Hackathon TODO - Phase I: Console App

Task management CLI application built with Python using clean architecture and spec-driven development.

## Quick Start

```bash
# Run the CLI
python3 todo.py --help

# Create a task
python3 todo.py add "Buy milk" --description "From the grocery store"

# List all tasks
python3 todo.py list

# Update a task
python3 todo.py update 1 --title "Buy almond milk"

# Mark task complete
python3 todo.py complete 1

# Delete a task
python3 todo.py delete 1
```

## Requirements

- Python 3.13+
- Standard library only (no external dependencies)

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create new task | `todo.py add "Title" --description "Desc"` |
| `list` | View all tasks | `todo.py list` |
| `update` | Update task | `todo.py update 1 --title "New title"` |
| `delete` | Delete task | `todo.py delete 1` |
| `complete` | Mark complete | `todo.py complete 1` |
| `--help` | Show help | `todo.py --help` |
| `--version` | Show version | `todo.py --version` |

## Project Structure

```
.
├── todo.py                          # CLI entry point
├── src/
│   ├── domain/
│   │   ├── task.py                  # Task entity, TaskStatus enum
│   │   ├── repository.py            # TaskRepository interface
│   │   └── exceptions.py            # Custom exceptions
│   ├── infrastructure/
│   │   └── in_memory_repository.py  # In-memory implementation
│   └── cli/
│       ├── main.py                  # Argument parsing
│       ├── commands.py              # Command handlers
│       └── formatters.py            # Output formatting
├── tests/
│   ├── test_domain/
│   │   ├── test_task.py
│   │   └── test_exceptions.py
│   ├── test_infrastructure/
│   │   └── test_in_memory_repository.py
│   └── test_cli/
│       ├── test_commands.py
│       ├── test_formatters.py
│       └── test_main.py
└── specs/
    ├── features/
    │   ├── task-crud.md             # Feature specification
    │   ├── task-crud-plan.md        # Architecture plan
    │   └── task-crud-tasks.md       # Implementation tasks
```

## Running Tests

```bash
# Run all tests
python3 -m unittest discover -s tests -v

# Run specific test module
python3 -m unittest tests.test_domain.test_task -v
```

## Architecture

Follows **Clean Architecture** principles:

- **Domain Layer**: Business logic (Task entity, Repository interface)
- **Infrastructure Layer**: Implementation details (In-memory storage)
- **CLI Layer**: User interface (Commands, formatting)

### Key Design Decisions

- **In-Memory Storage**: Tasks are not persisted (Phase I constraint)
- **Auto-increment IDs**: Unique integer IDs starting from 1
- **ID Non-Reuse**: Deleted task IDs are not reused
- **Validation**: Title (1-200 chars), Description (0-1000 chars)
- **Timestamps**: UTC datetime for created_at and completed_at

## Specifications

- [Feature Spec](specs/features/task-crud.md)
- [Architecture Plan](specs/features/task-crud-plan.md)
- [Implementation Tasks](specs/features/task-crud-tasks.md)

## Test Coverage

- **Domain Layer**: 100% (Task entity, exceptions, repository interface)
- **Infrastructure Layer**: 100% (In-memory repository)
- **CLI Layer**: 80%+ (Commands, formatters, integration)
- **Total**: 63 tests

## Phase I Constraints

- No data persistence (in-memory only)
- Standard library only
- Single-user CLI interface
- No task filtering or sorting

## Next Phase

Phase II will add:
- File/database persistence
- Web API backend
- Frontend UI

## License

MIT
