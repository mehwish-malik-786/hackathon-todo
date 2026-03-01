"""
Tests for AI Chatbot chat API.

Test natural language commands:
- "Add task buy milk tomorrow"
- "Summarize my tasks"
- "Delete task 3"
- "Mark task 1 as done"
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from main import app
from models.task import Task
from models.conversation import Conversation
from models.message import Message


# Test database
@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with dependency overrides."""
    def get_session():
        yield session
    
    app.dependency_overrides["get_session"] = get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestChatAPI:
    """Test chat endpoint functionality."""

    def test_chat_health(self, client: TestClient):
        """Test chat health endpoint."""
        response = client.get("/api/chat/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_create_task(self, client: TestClient, session: Session):
        """Test creating task via natural language."""
        response = client.post(
            "/api/chat",
            json={
                "message": "Add task buy milk tomorrow",
                "session_id": "test-session-1"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "task_created"
        assert "task" in data
        assert data["task"]["title"] == "Buy milk tomorrow"
        assert data["metadata"]["intent"] == "create_task"

    def test_chat_list_tasks(self, client: TestClient, session: Session):
        """Test listing tasks via natural language."""
        # First create a task
        client.post(
            "/api/chat",
            json={
                "message": "Add task test task",
                "session_id": "test-session-2"
            }
        )
        
        # Then list tasks
        response = client.post(
            "/api/chat",
            json={
                "message": "Show my tasks",
                "session_id": "test-session-2"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "tasks_listed"
        assert "tasks" in data
        assert data["metadata"]["intent"] == "list_tasks"

    def test_chat_summarize_tasks(self, client: TestClient, session: Session):
        """Test summarizing tasks via natural language."""
        response = client.post(
            "/api/chat",
            json={
                "message": "Summarize my tasks",
                "session_id": "test-session-3"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "tasks_summarized"
        assert data["metadata"]["intent"] == "summarize_tasks"

    def test_chat_complete_task(self, client: TestClient, session: Session):
        """Test completing task via natural language."""
        # First create a task
        create_response = client.post(
            "/api/chat",
            json={
                "message": "Add task test completion",
                "session_id": "test-session-4"
            }
        )
        task_id = create_response.json()["task"]["id"]
        
        # Then complete it
        response = client.post(
            "/api/chat",
            json={
                "message": f"Mark task {task_id} as done",
                "session_id": "test-session-4"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "task_completed"
        assert data["metadata"]["intent"] == "complete_task"

    def test_chat_delete_task(self, client: TestClient, session: Session):
        """Test deleting task via natural language."""
        # First create a task
        create_response = client.post(
            "/api/chat",
            json={
                "message": "Add task test delete",
                "session_id": "test-session-5"
            }
        )
        task_id = create_response.json()["task"]["id"]
        
        # Then delete it
        response = client.post(
            "/api/chat",
            json={
                "message": f"Delete task {task_id}",
                "session_id": "test-session-5"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "task_deleted"
        assert data["metadata"]["intent"] == "delete_task"

    def test_chat_help(self, client: TestClient, session: Session):
        """Test help command."""
        response = client.post(
            "/api/chat",
            json={
                "message": "Help",
                "session_id": "test-session-6"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["action"] == "help_provided"
        assert data["metadata"]["intent"] == "help"

    def test_chat_unknown_intent(self, client: TestClient, session: Session):
        """Test unknown command handling."""
        response = client.post(
            "/api/chat",
            json={
                "message": "Random gibberish xyz123",
                "session_id": "test-session-7"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["intent"] == "unknown"

    def test_conversation_history(self, client: TestClient, session: Session):
        """Test getting conversation history."""
        session_id = "test-session-history"
        
        # Send a message
        client.post(
            "/api/chat",
            json={
                "message": "Add task test history",
                "session_id": session_id
            }
        )
        
        # Get history
        response = client.get(f"/api/chat/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == session_id
        assert len(data["messages"]) >= 2  # User message + AI response
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"


class TestAIAgent:
    """Test AI agent intent classification."""

    def test_parse_create_task_intent(self):
        """Test create task intent detection."""
        from services.ai_agent import QwenAIAgent
        
        agent = QwenAIAgent()
        result = agent.process_message("Add task buy milk tomorrow")
        
        assert result["intent"] == "create_task"
        assert "title" in result["data"]

    def test_parse_list_tasks_intent(self):
        """Test list tasks intent detection."""
        from services.ai_agent import QwenAIAgent
        
        agent = QwenAIAgent()
        result = agent.process_message("Show my pending tasks")
        
        assert result["intent"] == "list_tasks"

    def test_parse_complete_task_intent(self):
        """Test complete task intent detection."""
        from services.ai_agent import QwenAIAgent
        
        agent = QwenAIAgent()
        result = agent.process_message("Mark task 5 as done")
        
        assert result["intent"] == "complete_task"
        assert result["data"]["task_id"] == 5

    def test_parse_delete_task_intent(self):
        """Test delete task intent detection."""
        from services.ai_agent import QwenAIAgent
        
        agent = QwenAIAgent()
        result = agent.process_message("Delete task 3")
        
        assert result["intent"] == "delete_task"
        assert result["data"]["task_id"] == 3

    def test_parse_summarize_intent(self):
        """Test summarize intent detection."""
        from services.ai_agent import QwenAIAgent
        
        agent = QwenAIAgent()
        result = agent.process_message("Summarize my tasks")
        
        assert result["intent"] == "summarize_tasks"
