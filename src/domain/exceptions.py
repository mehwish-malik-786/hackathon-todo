"""Domain layer: Custom exceptions."""


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
