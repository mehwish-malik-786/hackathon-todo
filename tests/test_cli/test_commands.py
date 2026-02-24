"""Tests for CLI layer: Command handlers."""
import io
import sys
import unittest
from src.domain.task import Task, TaskStatus
from src.infrastructure.in_memory_repository import InMemoryTaskRepository
from src.domain.exceptions import TaskNotFoundError
from src.cli.commands import handle_add, handle_list, handle_update, handle_delete, handle_complete


class TestCommandHandlers(unittest.TestCase):
    """Test cases for command handlers."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo = InMemoryTaskRepository()
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        """Restore stdout."""
        sys.stdout = self.old_stdout

    def get_output(self):
        """Get captured stdout."""
        return sys.stdout.getvalue()

    def test_handle_add_title_only(self):
        """Test adding task with title only."""
        handle_add(self.repo, "Test Task", None)
        output = self.get_output()
        
        tasks = self.repo.get_all()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Test Task")
        self.assertIn("✓", output)

    def test_handle_add_with_description(self):
        """Test adding task with description."""
        handle_add(self.repo, "Test Task", "Test description")
        
        tasks = self.repo.get_all()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Test description")

    def test_handle_list_empty(self):
        """Test listing empty repository."""
        handle_list(self.repo)
        output = self.get_output()
        self.assertIn("No tasks", output)

    def test_handle_list_with_tasks(self):
        """Test listing with tasks."""
        self.repo.add(Task(title="Task 1"))
        handle_list(self.repo)
        output = self.get_output()
        self.assertIn("Task 1", output)

    def test_handle_update_title(self):
        """Test updating task title."""
        self.repo.add(Task(title="Original"))
        handle_update(self.repo, 1, title="Updated")
        
        task = self.repo.get_by_id(1)
        self.assertEqual(task.title, "Updated")

    def test_handle_update_description(self):
        """Test updating task description."""
        self.repo.add(Task(title="Test", description="Original"))
        handle_update(self.repo, 1, description="Updated")
        
        task = self.repo.get_by_id(1)
        self.assertEqual(task.description, "Updated")

    def test_handle_update_both(self):
        """Test updating both title and description."""
        self.repo.add(Task(title="Original", description="Original desc"))
        handle_update(self.repo, 1, title="New Title", description="New Desc")
        
        task = self.repo.get_by_id(1)
        self.assertEqual(task.title, "New Title")
        self.assertEqual(task.description, "New Desc")

    def test_handle_update_not_found_raises(self):
        """Test updating non-existent task raises error."""
        with self.assertRaises(TaskNotFoundError):
            handle_update(self.repo, 999, title="Bad")

    def test_handle_delete_existing(self):
        """Test deleting existing task."""
        self.repo.add(Task(title="Test"))
        handle_delete(self.repo, 1)
        
        self.assertIsNone(self.repo.get_by_id(1))
        output = self.get_output()
        self.assertIn("deleted", output.lower())

    def test_handle_delete_not_found_raises(self):
        """Test deleting non-existent task raises error."""
        with self.assertRaises(TaskNotFoundError):
            handle_delete(self.repo, 999)

    def test_handle_complete_existing(self):
        """Test completing existing task."""
        self.repo.add(Task(title="Test"))
        handle_complete(self.repo, 1)
        
        task = self.repo.get_by_id(1)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)

    def test_handle_complete_not_found_raises(self):
        """Test completing non-existent task raises error."""
        with self.assertRaises(TaskNotFoundError):
            handle_complete(self.repo, 999)


if __name__ == "__main__":
    unittest.main()
