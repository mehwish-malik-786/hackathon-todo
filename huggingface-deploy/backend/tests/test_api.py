import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_session, engine
from sqlmodel import SQLModel, Session
from models.task import Task


@pytest.fixture(scope="module")
def client():
    """Create test client with in-memory database."""
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    def override_get_session():
        try:
            session = Session(engine)
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


class TestTaskAPI:
    """Test suite for Task API endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_list_tasks_empty(self, client: TestClient):
        """Test listing tasks when empty."""
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task_title_only(self, client: TestClient):
        """Test creating a task with title only."""
        response = client.post(
            "/tasks",
            json={"title": "Test Task"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] is None
        assert data["status"] == "pending"
        assert data["id"] is not None

    def test_create_task_with_description(self, client: TestClient):
        """Test creating a task with title and description."""
        response = client.post(
            "/tasks",
            json={"title": "Test Task", "description": "Test Description"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Test Description"

    def test_create_task_validation_error(self, client: TestClient):
        """Test creating a task with empty title."""
        response = client.post(
            "/tasks",
            json={"title": ""}
        )
        assert response.status_code == 422

    def test_create_task_missing_title(self, client: TestClient):
        """Test creating a task without title."""
        response = client.post(
            "/tasks",
            json={"description": "Test Description"}
        )
        assert response.status_code == 422

    def test_get_task_found(self, client: TestClient):
        """Test getting a task that exists."""
        # Create task first
        create_response = client.post("/tasks", json={"title": "Get Test"})
        task_id = create_response.json()["id"]
        
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Get Test"

    def test_get_task_not_found(self, client: TestClient):
        """Test getting a task that doesn't exist."""
        response = client.get("/tasks/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_task_title(self, client: TestClient):
        """Test updating task title."""
        create_response = client.post("/tasks", json={"title": "Original"})
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_update_task_description(self, client: TestClient):
        """Test updating task description."""
        create_response = client.post("/tasks", json={"title": "Test"})
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/tasks/{task_id}",
            json={"description": "New Description"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New Description"

    def test_update_task_not_found(self, client: TestClient):
        """Test updating a task that doesn't exist."""
        response = client.put(
            "/tasks/999",
            json={"title": "Updated"}
        )
        assert response.status_code == 404

    def test_delete_task(self, client: TestClient):
        """Test deleting a task."""
        create_response = client.post("/tasks", json={"title": "Delete Me"})
        task_id = create_response.json()["id"]
        
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/tasks/999")
        assert response.status_code == 404

    def test_complete_task(self, client: TestClient):
        """Test marking a task as complete."""
        create_response = client.post("/tasks", json={"title": "Complete Me"})
        task_id = create_response.json()["id"]
        
        response = client.patch(f"/tasks/{task_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_complete_task_not_found(self, client: TestClient):
        """Test completing a task that doesn't exist."""
        response = client.patch("/tasks/999/complete")
        assert response.status_code == 404

    def test_full_crud_flow(self, client: TestClient):
        """Test complete CRUD flow."""
        # Create
        create_response = client.post(
            "/tasks",
            json={"title": "Flow Test", "description": "Testing CRUD"}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Read
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        
        # Update
        update_response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Flow Test Updated"}
        )
        assert update_response.status_code == 200
        
        # Complete
        complete_response = client.patch(f"/tasks/{task_id}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"
        
        # List
        list_response = client.get("/tasks")
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1
        
        # Delete
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 204
