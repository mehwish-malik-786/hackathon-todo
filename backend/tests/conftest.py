import pytest
from sqlmodel import SQLModel, create_engine, Session
from database import get_settings
from models.task import Task


@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite database for testing."""
    settings = get_settings()
    # Use SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        echo=True,
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a new database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def repository(session):
    """Create task repository instance."""
    from repositories.task_repository import TaskRepository
    return TaskRepository(session)


@pytest.fixture
def sample_task(session):
    """Create a sample task for testing."""
    task = Task(title="Test Task", description="Test Description")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
