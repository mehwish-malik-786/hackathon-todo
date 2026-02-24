"""CLI layer: Output formatting utilities."""
from datetime import datetime
from typing import List
from src.domain.task import Task, TaskStatus


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
