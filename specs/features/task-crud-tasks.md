# Task CRUD Implementation Tasks

**Feature**: Task CRUD Operations  
**Spec Reference**: `specs/features/task-crud.md`  
**Plan Reference**: `specs/features/task-crud-plan.md`  
**Phase**: Phase I (Console Todo App)  
**Priority**: P0

---

## Task Summary

| ID | Task | Layer | Dependencies |
|----|------|-------|--------------|
| T001 | Create project structure | Setup | None |
| T002 | Implement TaskStatus enum | Domain | T001 |
| T003 | Implement Task entity | Domain | T002 |
| T004 | Implement custom exceptions | Domain | T001 |
| T005 | Implement TaskRepository ABC | Domain | T001 |
| T006 | Implement InMemoryTaskRepository | Infrastructure | T005 |
| T007 | Implement output formatters | CLI | T003 |
| T008 | Implement command handlers | CLI | T006, T007 |
| T009 | Implement CLI main entry point | CLI | T008 |
| T010 | Create root entry point script | CLI | T009 |
| T011 | Write Task entity tests | Tests | T003 |
| T012 | Write exceptions tests | Tests | T004 |
| T013 | Write repository tests | Tests | T006 |
| T014 | Write formatter tests | Tests | T007 |
| T015 | Write command handler tests | Tests | T008 |
| T016 | Write CLI integration tests | Tests | T010 |
| T017 | Run all tests and verify coverage | QA | T011-T016 |

---

## Implementation Tasks

### T001: Create Project Structure

**Spec Reference**: `specs/features/task-crud-plan.md` §5 (Folder Structure)

**Expected Output**:
- Directory structure created:
  - `src/`, `src/domain/`, `src/infrastructure/`, `src/cli/`
  - `tests/`, `tests/test_domain/`, `tests/test_infrastructure/`, `tests/test_cli/`
- `__init__.py` files in all packages
- `todo.py` entry point stub at project root

**Validation Step**:
```bash
# Verify directory structure
test -d src/domain && test -d src/infrastructure && test -d src/cli && \
test -d tests/test_domain && test -d tests/test_infrastructure && test -d tests/test_cli && \
echo "✓ All directories exist"

# Verify __init__.py files
find src tests -name "__init__.py" | wc -l  # Should return 8

# Verify todo.py exists
test -f todo.py && echo "✓ todo.py exists"
```

---

### T002: Implement TaskStatus Enum

**Spec Reference**: `specs/features/task-crud-plan.md` §2.1

**Expected Output**:
- `src/domain/task.py` with `TaskStatus` enum
- Two values: `PENDING = "pending"`, `COMPLETED = "completed"`

**Validation Step**:
```bash
# Verify enum values
python3 -c "from src.domain.task import TaskStatus; assert TaskStatus.PENDING.value == 'pending'; assert TaskStatus.COMPLETED.value == 'completed'; print('✓ TaskStatus enum valid')"
```

---

### T003: Implement Task Entity

**Spec Reference**: `specs/features/task-crud-plan.md` §2.1, `specs/features/task-crud.md` §Technical Specifications (Domain Model)

**Expected Output**:
- `Task` dataclass with fields: id, title, description, status, created_at, completed_at
- `__post_init__` validation for title (1-200 chars, non-empty) and description (0-1000 chars)
- `mark_complete()` method sets status and completed_at
- `to_dict()` method returns dictionary representation

**Validation Step**:
```bash
# Verify Task creation and validation
python3 << 'EOF'
from src.domain.task import Task, TaskStatus
from datetime import datetime

# Valid task
t = Task(title="Test")
assert t.id == 0, "Default ID should be 0"
assert t.status == TaskStatus.PENDING
assert t.description is None
assert isinstance(t.created_at, datetime)
assert t.completed_at is None

# Task with description
t2 = Task(title="Test", description="Desc")
assert t2.description == "Desc"

# Empty description becomes None
t3 = Task(title="Test", description="")
assert t3.description is None

# Validation: empty title
try:
    Task(title="")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Validation: whitespace title
try:
    Task(title="   ")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Validation: title too long
try:
    Task(title="x" * 201)
    assert False, "Should raise ValueError"
except ValueError:
    pass

# mark_complete
t.mark_complete()
assert t.status == TaskStatus.COMPLETED
assert t.completed_at is not None

# to_dict
d = t.to_dict()
assert d["status"] == "completed"
assert d["title"] == "Test"

print("✓ Task entity validation passed")
EOF
```

---

### T004: Implement Custom Exceptions

**Spec Reference**: `specs/features/task-crud-plan.md` §2.3

**Expected Output**:
- `src/domain/exceptions.py` with three exception classes
- `TaskError(Exception)` - base class
- `TaskNotFoundError(TaskError)` - stores task_id, message includes ID
- `TaskValidationError(TaskError)` - stores message

**Validation Step**:
```bash
# Verify exception classes
python3 << 'EOF'
from src.domain.exceptions import TaskError, TaskNotFoundError, TaskValidationError

# TaskNotFoundError
try:
    raise TaskNotFoundError(5)
except TaskNotFoundError as e:
    assert "5" in str(e), "Message should contain task ID"
    assert e.task_id == 5

# TaskValidationError
try:
    raise TaskValidationError("invalid title")
except TaskValidationError as e:
    assert "invalid title" in str(e)

# Inheritance
assert issubclass(TaskNotFoundError, TaskError)
assert issubclass(TaskValidationError, TaskError)

print("✓ Exception classes validation passed")
EOF
```

---

### T005: Implement TaskRepository ABC

**Spec Reference**: `specs/features/task-crud-plan.md` §2.2, `specs/features/task-crud.md` §Technical Specifications (Repository Interface)

**Expected Output**:
- `src/domain/repository.py` with abstract `TaskRepository` class
- Five abstract methods: `add`, `get_by_id`, `get_all`, `update`, `delete`
- Proper type hints and docstrings

**Validation Step**:
```bash
# Verify ABC cannot be instantiated
python3 << 'EOF'
from src.domain.repository import TaskRepository

try:
    TaskRepository()
    assert False, "Should not be able to instantiate ABC"
except TypeError:
    pass  # Expected

# Verify methods are defined
import inspect
methods = ['add', 'get_by_id', 'get_all', 'update', 'delete']
for method in methods:
    assert hasattr(TaskRepository, method), f"Missing method: {method}"
    assert getattr(inspect, 'ismethod')(getattr(TaskRepository, method)) or \
           getattr(inspect, 'isfunction')(getattr(TaskRepository, method))

print("✓ TaskRepository ABC validation passed")
EOF
```

---

### T006: Implement InMemoryTaskRepository

**Spec Reference**: `specs/features/task-crud-plan.md` §3.1

**Expected Output**:
- `src/infrastructure/in_memory_repository.py`
- `InMemoryTaskRepository` class implementing `TaskRepository`
- Internal storage: `Dict[int, Task]`
- Auto-increment ID starting at 1
- ID not reused after deletion

**Validation Step**:
```bash
# Verify repository implementation
python3 << 'EOF'
from src.domain.task import Task
from src.infrastructure.in_memory_repository import InMemoryTaskRepository
from src.domain.exceptions import TaskNotFoundError

repo = InMemoryTaskRepository()

# Empty repository
assert repo.get_all() == []
assert repo.get_by_id(1) is None

# Add task
t1 = Task(title="Task 1")
result = repo.add(t1)
assert result.id == 1
assert repo.get_by_id(1) is not None

# Add second task - unique ID
t2 = Task(title="Task 2")
result2 = repo.add(t2)
assert result2.id == 2

# Get all - in order
all_tasks = repo.get_all()
assert len(all_tasks) == 2
assert all_tasks[0].id == 1
assert all_tasks[1].id == 2

# Update
t1.title = "Updated Task 1"
updated = repo.update(t1)
assert updated.title == "Updated Task 1"

# Update non-existent
try:
    bad_task = Task(title="Bad")
    bad_task.id = 999
    repo.update(bad_task)
    assert False, "Should raise TaskNotFoundError"
except TaskNotFoundError:
    pass

# Delete
assert repo.delete(1) == True
assert repo.get_by_id(1) is None

# Delete non-existent
assert repo.delete(999) == False

# Delete invalid ID
try:
    repo.delete(-1)
    assert False, "Should raise ValueError"
except ValueError:
    pass

try:
    repo.delete(0)
    assert False, "Should raise ValueError"
except ValueError:
    pass

# ID not reused after deletion
t3 = Task(title="Task 3")
result3 = repo.add(t3)
assert result3.id == 3  # Not reusing ID 1

print("✓ InMemoryTaskRepository validation passed")
EOF
```

---

### T007: Implement Output Formatters

**Spec Reference**: `specs/features/task-crud-plan.md` §4.5

**Expected Output**:
- `src/cli/formatters.py` with three functions
- `format_task(task)` - single task with status icon
- `format_task_list(tasks)` - multiple tasks with timestamps
- `format_datetime(dt)` - readable datetime format

**Validation Step**:
```bash
# Verify formatters
python3 << 'EOF'
from src.domain.task import Task, TaskStatus
from src.cli.formatters import format_task, format_task_list, format_datetime

# Create test tasks
pending = Task(title="Buy milk", description="From store")
pending.id = 1

completed = Task(title="Pay bills")
completed.id = 2
completed.mark_complete()

# format_task - pending
pending_str = format_task(pending)
assert "[1]" in pending_str
assert "○" in pending_str  # Pending icon
assert "Buy milk" in pending_str
assert "From store" in pending_str

# format_task - completed
completed_str = format_task(completed)
assert "✓" in completed_str  # Completed icon

# format_task - no description
no_desc = Task(title="Simple task")
no_desc.id = 3
no_desc_str = format_task(no_desc)
assert " - " not in no_desc_str or no_desc.description is None

# format_task_list
list_str = format_task_list([pending, completed])
assert "Created:" in list_str
assert "Completed:" in list_str  # For completed task

# Empty list
empty_str = format_task_list([])
assert empty_str == ""

# format_datetime
from datetime import datetime
dt_str = format_datetime(datetime(2026, 2, 24, 10, 30, 45))
assert dt_str == "2026-02-24 10:30:45"

print("✓ Formatters validation passed")
EOF
```

---

### T008: Implement Command Handlers

**Spec Reference**: `specs/features/task-crud-plan.md` §4.4, `specs/features/task-crud.md` §User Stories (US-001 through US-005)

**Expected Output**:
- `src/cli/commands.py` with five handler functions
- `handle_add(repo, title, description)` - creates task, prints success
- `handle_list(repo)` - lists tasks or "No tasks" message
- `handle_update(repo, id, title, description)` - updates fields
- `handle_delete(repo, id)` - deletes task
- `handle_complete(repo, id)` - marks complete

**Validation Step**:
```bash
# Verify command handlers
python3 << 'EOF'
import io
import sys
from src.domain.task import Task
from src.infrastructure.in_memory_repository import InMemoryTaskRepository
from src.domain.exceptions import TaskNotFoundError
from src.cli.commands import handle_add, handle_list, handle_update, handle_delete, handle_complete

repo = InMemoryTaskRepository()

# Capture stdout
old_stdout = sys.stdout
sys.stdout = io.StringIO()

# handle_add
handle_add(repo, "Test Task", "Test description")
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "✓" in output or "Task created" in output

# Verify task was added
tasks = repo.get_all()
assert len(tasks) == 1
assert tasks[0].title == "Test Task"

# handle_list with tasks
sys.stdout = io.StringIO()
handle_list(repo)
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "Test Task" in output

# Empty repository message
empty_repo = InMemoryTaskRepository()
sys.stdout = io.StringIO()
handle_list(empty_repo)
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "No tasks" in output

# handle_update
sys.stdout = io.StringIO()
handle_update(repo, 1, title="Updated Title")
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "Updated" in output
assert repo.get_by_id(1).title == "Updated Title"

# handle_update non-existent
try:
    handle_update(repo, 999, title="Bad")
    assert False, "Should raise TaskNotFoundError"
except TaskNotFoundError:
    pass

# handle_delete
sys.stdout = io.StringIO()
handle_delete(repo, 1)
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "deleted" in output.lower()
assert repo.get_by_id(1) is None

# handle_delete non-existent
try:
    handle_delete(repo, 999)
    assert False, "Should raise TaskNotFoundError"
except TaskNotFoundError:
    pass

# handle_complete - add new task first
handle_add(repo, "To Complete", None)
sys.stdout = io.StringIO()
handle_complete(repo, 2)
output = sys.stdout.getvalue()
sys.stdout = old_stdout
assert "completed" in output.lower()
assert repo.get_by_id(2).status.value == "completed"

# handle_complete non-existent
try:
    handle_complete(repo, 999)
    assert False, "Should raise TaskNotFoundError"
except TaskNotFoundError:
    pass

print("✓ Command handlers validation passed")
EOF
```

---

### T009: Implement CLI Main Entry Point

**Spec Reference**: `specs/features/task-crud-plan.md` §4.3, `specs/features/task-crud.md` §Technical Specifications (CLI Commands)

**Expected Output**:
- `src/cli/main.py` with `main()` and `create_parser()` functions
- argparse configuration for all commands
- Proper exit codes (0=success, 1=error, 2=argparse error)
- Error messages to stderr

**Validation Step**:
```bash
# Verify CLI entry point
python3 << 'EOF'
from src.cli.main import main

# Test --version
try:
    main(["--version"])
except SystemExit as e:
    assert e.code == 0

# Test --help
try:
    main(["--help"])
except SystemExit as e:
    assert e.code == 0

# Test no command - should show help and exit 1
try:
    main([])
except SystemExit as e:
    assert e.code == 1

# Test invalid command - should exit 2
try:
    main(["invalid"])
except SystemExit as e:
    assert e.code == 2

# Test add command - should exit 0
exit_code = main(["add", "Test Task"])
assert exit_code == 0

# Test list command - should exit 0
exit_code = main(["list"])
assert exit_code == 0

# Test update with non-existent ID - should exit 1
exit_code = main(["update", "999", "--title", "Bad"])
assert exit_code == 1

# Test delete with non-existent ID - should exit 1
exit_code = main(["delete", "999"])
assert exit_code == 1

# Test complete with non-existent ID - should exit 1
exit_code = main(["complete", "999"])
assert exit_code == 1

print("✓ CLI main entry point validation passed")
EOF
```

---

### T010: Create Root Entry Point Script

**Spec Reference**: `specs/features/task-crud-plan.md` §5.1

**Expected Output**:
- `todo.py` at project root
- Shebang: `#!/usr/bin/env python3`
- Imports and calls `src.cli.main.main()`
- Executable permission

**Validation Step**:
```bash
# Verify todo.py entry point
python3 todo.py --help && echo "✓ todo.py --help works"
python3 todo.py --version && echo "✓ todo.py --version works"
python3 todo.py add "Test" && echo "✓ todo.py add works"
python3 todo.py list && echo "✓ todo.py list works"

# Verify executable permission
test -x todo.py || chmod +x todo.py
./todo.py --help && echo "✓ Direct execution works"
```

---

## Test Tasks

### T011: Write Task Entity Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (Domain Layer Tests - Task entity tests)

**Expected Output**:
- `tests/test_domain/test_task.py` with `TestTask` class
- 13 test methods covering all Task functionality

**Test Cases**:
- [ ] `test_create_task_title_only`
- [ ] `test_create_task_with_description`
- [ ] `test_task_id_default_zero`
- [ ] `test_task_default_status_pending`
- [ ] `test_task_created_at_datetime`
- [ ] `test_task_completed_at_none`
- [ ] `test_mark_complete`
- [ ] `test_title_empty_string_raises`
- [ ] `test_title_whitespace_only_raises`
- [ ] `test_title_too_long_raises`
- [ ] `test_description_too_long_raises`
- [ ] `test_description_empty_becomes_none`
- [ ] `test_to_dict`

**Validation Step**:
```bash
# Run Task entity tests
python3 -m unittest tests.test_domain.test_task -v
# Expected: 13 tests, 0 failures
```

---

### T012: Write Exceptions Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (Domain Layer Tests - Exception tests)

**Expected Output**:
- `tests/test_domain/test_exceptions.py` with test class
- 2 test methods for exception behavior

**Test Cases**:
- [ ] `test_task_not_found_error_message`
- [ ] `test_task_validation_error_message`

**Validation Step**:
```bash
# Run exceptions tests
python3 -m unittest tests.test_domain.test_exceptions -v
# Expected: 2 tests, 0 failures
```

---

### T013: Write Repository Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (Infrastructure Layer Tests)

**Expected Output**:
- `tests/test_infrastructure/test_in_memory_repository.py` with test class
- 12 test methods covering repository operations

**Test Cases**:
- [ ] `test_add_assigns_id`
- [ ] `test_add_increments_id`
- [ ] `test_get_by_id_found`
- [ ] `test_get_by_id_not_found`
- [ ] `test_get_by_id_invalid_raises`
- [ ] `test_get_all_empty`
- [ ] `test_get_all_order`
- [ ] `test_update_existing`
- [ ] `test_update_nonexistent_raises`
- [ ] `test_delete_existing`
- [ ] `test_delete_nonexistent_returns_false`
- [ ] `test_delete_invalid_raises`

**Validation Step**:
```bash
# Run repository tests
python3 -m unittest tests.test_infrastructure.test_in_memory_repository -v
# Expected: 12 tests, 0 failures
```

---

### T014: Write Formatter Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (CLI Layer Tests - Formatter tests)

**Expected Output**:
- `tests/test_cli/test_formatters.py` with test class
- 6 test methods for formatter functions

**Test Cases**:
- [ ] `test_format_task_pending_icon`
- [ ] `test_format_task_completed_icon`
- [ ] `test_format_task_with_description`
- [ ] `test_format_task_without_description`
- [ ] `test_format_task_list_multiple`
- [ ] `test_format_datetime_format`

**Validation Step**:
```bash
# Run formatter tests
python3 -m unittest tests.test_cli.test_formatters -v
# Expected: 6 tests, 0 failures
```

---

### T015: Write Command Handler Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (CLI Layer Tests - Command handler tests)

**Expected Output**:
- `tests/test_cli/test_commands.py` with test class
- 12 test methods for command handlers

**Test Cases**:
- [ ] `test_handle_add_title_only`
- [ ] `test_handle_add_with_description`
- [ ] `test_handle_list_empty`
- [ ] `test_handle_list_with_tasks`
- [ ] `test_handle_update_title`
- [ ] `test_handle_update_description`
- [ ] `test_handle_update_both`
- [ ] `test_handle_update_not_found_raises`
- [ ] `test_handle_delete_existing`
- [ ] `test_handle_delete_not_found_raises`
- [ ] `test_handle_complete_existing`
- [ ] `test_handle_complete_not_found_raises`

**Validation Step**:
```bash
# Run command handler tests
python3 -m unittest tests.test_cli.test_commands -v
# Expected: 12 tests, 0 failures
```

---

### T016: Write CLI Integration Tests

**Spec Reference**: `specs/features/task-crud-plan.md` §6.3 (CLI Layer Tests - CLI integration tests)

**Expected Output**:
- `tests/test_cli/test_main.py` with test class
- 9 test methods for CLI integration

**Test Cases**:
- [ ] `test_main_add_command`
- [ ] `test_main_list_command`
- [ ] `test_main_update_command`
- [ ] `test_main_delete_command`
- [ ] `test_main_complete_command`
- [ ] `test_main_no_command_exits_1`
- [ ] `test_main_invalid_command_exits_2`
- [ ] `test_main_version_flag`
- [ ] `test_main_help_flag`

**Validation Step**:
```bash
# Run CLI integration tests
python3 -m unittest tests.test_cli.test_main -v
# Expected: 9 tests, 0 failures
```

---

### T017: Run All Tests and Verify Coverage

**Spec Reference**: `specs/features/task-crud.md` §Testing Requirements, `specs/features/task-crud-plan.md` §6

**Expected Output**:
- All tests pass (54+ tests)
- Coverage report showing ≥80% overall
- Domain layer: 100% coverage
- Infrastructure layer: 100% coverage

**Validation Step**:
```bash
# Run all tests
python3 -m unittest discover -s tests -v

# With coverage (if installed)
python3 -m coverage run -m unittest discover -s tests
python3 -m coverage report --show-missing

# Verify coverage threshold
python3 << 'EOF'
import subprocess
result = subprocess.run(
    ["python3", "-m", "coverage", "report"],
    capture_output=True, text=True
)
print(result.stdout)
# Check that TOTAL >= 80%
EOF
```

---

## Task Execution Order

```
Phase 1: Foundation (Domain Layer)
┌─────────────────────────────────────┐
│ T001 → T002 → T003 → T004 → T005   │
│                    ↓                │
│              T011, T012             │
└─────────────────────────────────────┘

Phase 2: Infrastructure
┌─────────────────────────────────────┐
│         T005 → T006 → T013          │
└─────────────────────────────────────┘

Phase 3: CLI Layer
┌─────────────────────────────────────┐
│ T003 → T007 → T014                  │
│ T006 → T008 → T015                  │
│         T009 → T016                 │
│              T010                   │
└─────────────────────────────────────┘

Phase 4: Verification
┌─────────────────────────────────────┐
│         T017 (All Tests)            │
└─────────────────────────────────────┘
```

---

## Definition of Done

A task is considered complete when:
- [ ] Code implemented per specification
- [ ] Validation step passes
- [ ] Tests written (for implementation tasks)
- [ ] No syntax errors
- [ ] Type hints present on public APIs
- [ ] Follows clean architecture (no cross-layer violations)

---

**Version**: 1.0.0  
**Created**: 2026-02-24  
**Author**: AI Assistant  
**Status**: Draft  
**Next**: Begin implementation with T001
