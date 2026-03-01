from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from models.message import Message


class MessageRepository:
    """Repository for message database operations."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, conversation_id: int, role: str, content: str, 
            metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a new message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Created message with ID
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_by_conversation(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return

        Returns:
            List of messages ordered by creation date
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def get_latest(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """
        Get latest messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Number of recent messages to return

        Returns:
            List of recent messages
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(self.session.exec(statement).all()))
