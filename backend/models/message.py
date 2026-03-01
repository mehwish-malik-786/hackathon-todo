from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON


class Message(SQLModel, table=True):
    """
    Message domain model for chat messages.

    Represents a single message in a conversation.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(..., foreign_key="conversations.id", index=True)
    role: str = Field(..., max_length=20)  # 'user', 'assistant', 'system'
    content: str = Field(..., max_length=4000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    msg_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column("metadata", JSON))

    def to_dict(self) -> dict:
        """Convert message to dictionary representation."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "metadata": self.msg_metadata,
        }
