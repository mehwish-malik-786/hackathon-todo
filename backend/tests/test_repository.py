import pytest
from sqlmodel import Session
from models.task import Task, TaskStatus
from repositories.task_repository import TaskRepository


class TestTaskRepository:
    """Test suite for TaskRepository CRUD operations."""

    def test_add_task(self, repository: TaskRepository):
        """Test adding a new task."""
        task = Task(title="Test Task")
        result = repository.add(task)
        
        assert result.id is not None
        assert result.id > 0
        assert result.title == "Test Task"
        assert result.status == TaskStatus.PENDING

    def test_add_task_with_description(self, repository: TaskRepository):
        """Test adding a task with description."""
        task = Task(title="Test Task", description="Test Description")
        result = repository.add(task)
        
        assert result.description == "Test Description"

    def test_get_by_id_found(self, repository: TaskRepository, sample_task: Task):
        """Test getting a task by ID when it exists."""
        result = repository.get_by_id(sample_task.id)
        
        assert result is not None
        assert result.id == sample_task.id
        assert result.title == sample_task.title

    def test_get_by_id_not_found(self, repository: TaskRepository):
        """Test getting a task by ID when it doesn't exist."""
        result = repository.get_by_id(999)
        assert result is None

    def test_get_all_empty(self, repository: TaskRepository):
        """Test getting all tasks when repository is empty."""
        tasks = repository.get_all()
        assert len(tasks) == 0

    def test_get_all_multiple_tasks(self, repository: TaskRepository):
        """Test getting all tasks with multiple tasks."""
        repository.add(Task(title="Task 1"))
        repository.add(Task(title="Task 2"))
        repository.add(Task(title="Task 3"))
        
        tasks = repository.get_all()
        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"

    def test_update_existing(self, repository: TaskRepository, sample_task: Task):
        """Test updating an existing task."""
        sample_task.title = "Updated Title"
        sample_task.description = "Updated Description"
        
        result = repository.update(sample_task)
        
        assert result.title == "Updated Title"
        assert result.description == "Updated Description"

    def test_update_nonexistent(self, repository: TaskRepository):
        """Test updating a task that doesn't exist."""
        task = Task(id=999, title="Nonexistent")
        
        with pytest.raises(Exception):
            repository.update(task)

    def test_delete_existing(self, repository: TaskRepository, sample_task: Task):
        """Test deleting an existing task."""
        result = repository.delete(sample_task.id)
        
        assert result is True
        assert repository.get_by_id(sample_task.id) is None

    def test_delete_nonexistent(self, repository: TaskRepository):
        """Test deleting a task that doesn't exist."""
        result = repository.delete(999)
        assert result is False

    def test_mark_complete(self, repository: TaskRepository, sample_task: Task):
        """Test marking a task as complete."""
        sample_task.mark_complete()
        repository.update(sample_task)
        
        assert sample_task.status == TaskStatus.COMPLETED
        assert sample_task.completed_at is not None
