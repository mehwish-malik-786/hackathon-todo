"""Tests for domain layer: Task entity."""
import unittest
from datetime import datetime
from src.domain.task import Task, TaskStatus


class TestTask(unittest.TestCase):
    """Test cases for Task entity."""

    def test_create_task_title_only(self):
        """Test creating task with title only."""
        task = Task(title="Test Task")
        self.assertEqual(task.title, "Test Task")
        self.assertIsNone(task.description)
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_create_task_with_description(self):
        """Test creating task with title and description."""
        task = Task(title="Test Task", description="Test description")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test description")

    def test_task_id_default_zero(self):
        """Test that task ID defaults to 0."""
        task = Task(title="Test")
        self.assertEqual(task.id, 0)

    def test_task_default_status_pending(self):
        """Test that default status is PENDING."""
        task = Task(title="Test")
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_task_created_at_datetime(self):
        """Test that created_at is a datetime."""
        task = Task(title="Test")
        self.assertIsInstance(task.created_at, datetime)

    def test_task_completed_at_none(self):
        """Test that completed_at is None for new tasks."""
        task = Task(title="Test")
        self.assertIsNone(task.completed_at)

    def test_mark_complete(self):
        """Test marking task as complete."""
        task = Task(title="Test")
        task.mark_complete()
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.assertIsInstance(task.completed_at, datetime)

    def test_title_empty_string_raises(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="")

    def test_title_whitespace_only_raises(self):
        """Test that whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="   ")

    def test_title_too_long_raises(self):
        """Test that title > 200 chars raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="x" * 201)

    def test_description_too_long_raises(self):
        """Test that description > 1000 chars raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="Test", description="x" * 1001)

    def test_description_empty_becomes_none(self):
        """Test that empty description becomes None."""
        task = Task(title="Test", description="")
        self.assertIsNone(task.description)

    def test_to_dict(self):
        """Test to_dict returns correct dictionary."""
        task = Task(title="Test", description="Desc")
        task.id = 1
        task.mark_complete()
        
        result = task.to_dict()
        
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["title"], "Test")
        self.assertEqual(result["description"], "Desc")
        self.assertEqual(result["status"], "completed")
        self.assertIn("created_at", result)
        self.assertIn("completed_at", result)
        self.assertIsInstance(result["created_at"], str)
        self.assertIsInstance(result["completed_at"], str)


if __name__ == "__main__":
    unittest.main()
