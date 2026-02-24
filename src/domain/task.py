"""Domain layer: Task entity and status."""
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
