from typing import List, Optional
from sqlmodel import Session, select
from models.conversation import Conversation


class ConversationRepository:
    """Repository for conversation database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, session_id: str) -> Conversation:
        """
        Create a new conversation.

        Args:
            session_id: Session identifier

        Returns:
            Created conversation with ID
        """
        conversation = Conversation(session_id=session_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """
        Get conversation by session ID.

        Args:
            session_id: Session identifier

        Returns:
            Conversation if found, None otherwise
        """
        statement = select(Conversation).where(Conversation.session_id == session_id)
        return self.session.exec(statement).first()

    def get_or_create(self, session_id: str) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            session_id: Session identifier

        Returns:
            Existing or new conversation
        """
        conversation = self.get_by_session_id(session_id)
        if not conversation:
            conversation = self.create(session_id)
        return conversation

    def update_timestamp(self, conversation: Conversation) -> Conversation:
        """
        Update conversation timestamp.

        Args:
            conversation: Conversation to update

        Returns:
            Updated conversation
        """
        conversation.update_timestamp()
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation
