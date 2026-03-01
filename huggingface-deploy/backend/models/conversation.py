from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    """
    Conversation domain model for chat sessions.
    
    Represents a chat session between user and AI assistant.
    """
    
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(..., max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_timestamp(self):
        """Update the conversation's updated_at timestamp."""
        self.updated_at = datetime.utcnow()
