from sqlmodel import SQLModel, create_engine, Session
from config import get_settings

# Import all models to ensure they're registered with SQLModel
from models.task import Task
from models.conversation import Conversation
from models.message import Message

settings = get_settings()

# Neon PostgreSQL connection with connection pooling
engine = create_engine(
    settings.database_url,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
)


def create_db_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session generator for dependency injection."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
