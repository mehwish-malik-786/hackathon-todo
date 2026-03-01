from typing import List, Optional
from sqlmodel import Session, select
from models.task import Task


class TaskRepository:
    """Repository for task database operations."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> Task:
        """
        Add a new task to the database.
        
        Args:
            task: Task entity to add
            
        Returns:
            Task with assigned ID
        """
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, id: int) -> Optional[Task]:
        """
        Get task by unique ID.
        
        Args:
            id: Task unique identifier
            
        Returns:
            Task if found, None otherwise
        """
        return self.session.get(Task, id)

    def get_all(self) -> List[Task]:
        """
        Get all tasks ordered by creation date.
        
        Returns:
            List of all tasks
        """
        statement = select(Task).order_by(Task.created_at)
        return list(self.session.exec(statement).all())

    def update(self, task: Task) -> Task:
        """
        Update an existing task.
        
        Args:
            task: Task entity with updated fields
            
        Returns:
            Updated task
        """
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, id: int) -> bool:
        """
        Delete task by ID.
        
        Args:
            id: Task unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        task = self.get_by_id(id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False
