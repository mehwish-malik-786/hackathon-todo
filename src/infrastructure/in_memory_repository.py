"""Infrastructure layer: In-memory repository implementation."""
from typing import Dict, List, Optional
from src.domain.repository import TaskRepository
from src.domain.task import Task
from src.domain.exceptions import TaskNotFoundError


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
