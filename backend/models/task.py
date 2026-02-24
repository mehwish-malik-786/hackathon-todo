from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskStatus:
    """Task status constants."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Task domain model with database mapping.
    
    Represents a todo item with title, description, and status.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default=TaskStatus.PENDING, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

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
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
