"""Tests for domain layer: Custom exceptions."""
import unittest
from src.domain.exceptions import TaskError, TaskNotFoundError, TaskValidationError


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions."""

    def test_task_not_found_error_message(self):
        """Test TaskNotFoundError contains task ID in message."""
        error = TaskNotFoundError(5)
        self.assertEqual(error.task_id, 5)
        self.assertIn("5", str(error))
        self.assertIn("not found", str(error).lower())

    def test_task_validation_error_message(self):
        """Test TaskValidationError stores message."""
        error = TaskValidationError("invalid title")
        self.assertEqual(error.message, "invalid title")
        self.assertEqual(str(error), "invalid title")

    def test_task_not_found_is_task_error(self):
        """Test TaskNotFoundError inherits from TaskError."""
        error = TaskNotFoundError(1)
        self.assertIsInstance(error, TaskError)

    def test_task_validation_error_is_task_error(self):
        """Test TaskValidationError inherits from TaskError."""
        error = TaskValidationError("msg")
        self.assertIsInstance(error, TaskError)


if __name__ == "__main__":
    unittest.main()
