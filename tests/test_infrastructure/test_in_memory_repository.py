"""Tests for infrastructure layer: In-memory repository."""
import unittest
from src.domain.task import Task
from src.infrastructure.in_memory_repository import InMemoryTaskRepository
from src.domain.exceptions import TaskNotFoundError


class TestInMemoryTaskRepository(unittest.TestCase):
    """Test cases for InMemoryTaskRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo = InMemoryTaskRepository()

    def test_add_assigns_id(self):
        """Test that add assigns a non-zero ID."""
        task = Task(title="Test")
        result = self.repo.add(task)
        self.assertGreater(result.id, 0)

    def test_add_increments_id(self):
        """Test that each task gets a unique incrementing ID."""
        task1 = self.repo.add(Task(title="Task 1"))
        task2 = self.repo.add(Task(title="Task 2"))
        task3 = self.repo.add(Task(title="Task 3"))
        
        self.assertEqual(task1.id, 1)
        self.assertEqual(task2.id, 2)
        self.assertEqual(task3.id, 3)

    def test_get_by_id_found(self):
        """Test getting existing task by ID."""
        task = self.repo.add(Task(title="Test"))
        retrieved = self.repo.get_by_id(task.id)
        self.assertEqual(retrieved.title, "Test")

    def test_get_by_id_not_found(self):
        """Test getting non-existent task returns None."""
        result = self.repo.get_by_id(999)
        self.assertIsNone(result)

    def test_get_by_id_invalid_raises(self):
        """Test that invalid ID raises ValueError."""
        with self.assertRaises(ValueError):
            self.repo.get_by_id(-1)
        
        with self.assertRaises(ValueError):
            self.repo.get_by_id(0)

    def test_get_all_empty(self):
        """Test get_all returns empty list when no tasks."""
        result = self.repo.get_all()
        self.assertEqual(result, [])

    def test_get_all_order(self):
        """Test get_all returns tasks in ID order."""
        task3 = self.repo.add(Task(title="Task 3"))
        task1 = self.repo.add(Task(title="Task 1"))
        task2 = self.repo.add(Task(title="Task 2"))
        
        result = self.repo.get_all()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[1].id, 2)
        self.assertEqual(result[2].id, 3)

    def test_update_existing(self):
        """Test updating existing task."""
        task = self.repo.add(Task(title="Original"))
        task.title = "Updated"
        result = self.repo.update(task)
        self.assertEqual(result.title, "Updated")

    def test_update_nonexistent_raises(self):
        """Test updating non-existent task raises TaskNotFoundError."""
        task = Task(title="Test")
        task.id = 999
        with self.assertRaises(TaskNotFoundError):
            self.repo.update(task)

    def test_delete_existing(self):
        """Test deleting existing task."""
        task = self.repo.add(Task(title="Test"))
        result = self.repo.delete(task.id)
        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_id(task.id))

    def test_delete_nonexistent_returns_false(self):
        """Test deleting non-existent task returns False."""
        result = self.repo.delete(999)
        self.assertFalse(result)

    def test_delete_invalid_raises(self):
        """Test deleting invalid ID raises ValueError."""
        with self.assertRaises(ValueError):
            self.repo.delete(-1)
        
        with self.assertRaises(ValueError):
            self.repo.delete(0)

    def test_id_not_reused_after_deletion(self):
        """Test that IDs are not reused after deletion."""
        task1 = self.repo.add(Task(title="Task 1"))
        task2 = self.repo.add(Task(title="Task 2"))
        self.repo.delete(task1.id)
        task3 = self.repo.add(Task(title="Task 3"))
        
        # task3 should have ID 3, not reuse ID 1
        self.assertEqual(task3.id, 3)


if __name__ == "__main__":
    unittest.main()
