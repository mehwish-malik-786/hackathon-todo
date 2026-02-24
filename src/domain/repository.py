"""Domain layer: Repository interface for Task persistence."""
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
