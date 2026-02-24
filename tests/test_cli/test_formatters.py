"""Tests for CLI layer: Formatters."""
import unittest
from datetime import datetime
from src.domain.task import Task, TaskStatus
from src.cli.formatters import format_task, format_task_list, format_datetime


class TestFormatters(unittest.TestCase):
    """Test cases for output formatters."""

    def test_format_task_pending_icon(self):
        """Test pending task shows ○ icon."""
        task = Task(title="Test")
        task.id = 1
        result = format_task(task)
        self.assertIn("○", result)

    def test_format_task_completed_icon(self):
        """Test completed task shows ✓ icon."""
        task = Task(title="Test")
        task.id = 1
        task.mark_complete()
        result = format_task(task)
        self.assertIn("✓", result)

    def test_format_task_with_description(self):
        """Test task with description includes it."""
        task = Task(title="Test", description="Description")
        task.id = 1
        result = format_task(task)
        self.assertIn(" - Description", result)

    def test_format_task_without_description(self):
        """Test task without description doesn't show dash."""
        task = Task(title="Test")
        task.id = 1
        result = format_task(task)
        self.assertNotIn(" - ", result)

    def test_format_task_list_multiple(self):
        """Test formatting multiple tasks."""
        task1 = Task(title="Task 1")
        task1.id = 1
        task2 = Task(title="Task 2")
        task2.id = 2
        task2.mark_complete()
        
        result = format_task_list([task1, task2])
        
        self.assertIn("[1]", result)
        self.assertIn("[2]", result)
        self.assertIn("Task 1", result)
        self.assertIn("Task 2", result)

    def test_format_task_list_empty(self):
        """Test formatting empty list."""
        result = format_task_list([])
        self.assertEqual(result, "")

    def test_format_task_list_shows_timestamps(self):
        """Test that task list shows created timestamps."""
        task = Task(title="Test")
        task.id = 1
        result = format_task_list([task])
        self.assertIn("Created:", result)

    def test_format_task_list_completed_shows_completed_at(self):
        """Test that completed tasks show completed timestamp."""
        task = Task(title="Test")
        task.id = 1
        task.mark_complete()
        result = format_task_list([task])
        self.assertIn("Completed:", result)

    def test_format_datetime_format(self):
        """Test datetime format is YYYY-MM-DD HH:MM:SS."""
        dt = datetime(2026, 2, 24, 10, 30, 45)
        result = format_datetime(dt)
        self.assertEqual(result, "2026-02-24 10:30:45")


if __name__ == "__main__":
    unittest.main()
