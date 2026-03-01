from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""
    
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")


class TaskData(BaseModel):
    """Schema for task data in chat response."""
    
    id: int
    title: str
    description: Optional[str]
    status: str


class ChatResponse(BaseModel):
    """Schema for chat response."""
    
    response: str = Field(..., description="AI response message")
    action: Optional[str] = Field(default=None, description="Action performed (e.g., 'task_created', 'tasks_listed')")
    tasks: Optional[List[TaskData]] = Field(default=None, description="Tasks involved in response")
    task: Optional[TaskData] = Field(default=None, description="Single task involved")
    conversation_id: Optional[int] = Field(default=None, description="Conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class MessageResponse(BaseModel):
    """Schema for individual message in history."""
    
    id: int
    role: str
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history response."""
    
    session_id: str
    messages: List[MessageResponse]
