"""CLI layer: Command handlers."""
from typing import Optional
from src.domain.repository import TaskRepository
from src.domain.task import Task
from src.domain.exceptions import TaskNotFoundError
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
