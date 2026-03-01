from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Task description"
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(
        default=None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Task description"
    )


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
