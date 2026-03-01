"""
MCP (Model Context Protocol) Tools for Task Operations.

These tools allow the AI agent to interact with the task system:
- create_task
- list_tasks
- update_task
- delete_task
- complete_task
- summarize_tasks
"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate
from repositories.task_repository import TaskRepository


class MCPTaskTools:
    """
    MCP Tools for task operations.
    
    These tools are called by the AI agent to perform actions
    based on user's natural language commands.
    """
    
    def __init__(self, session: Session):
        """
        Initialize MCP tools with database session.
        
        Args:
            session: Database session
        """
        self.session = session
        self.repository = TaskRepository(session)
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task data or None if not found
        """
        task = self.repository.get_by_id(task_id)
        if task:
            return self._task_to_dict(task)
        return None

    def create_task(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Optional task description
            
        Returns:
            Created task as dictionary
        """
        task = Task(title=title, description=description)
        created_task = self.repository.add(task)
        
        return {
            "success": True,
            "action": "task_created",
            "task": self._task_to_dict(created_task),
        }
    
    def list_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List tasks with optional status filter.
        
        Args:
            status: Filter by status ('pending', 'completed', or None for all)
            
        Returns:
            List of tasks
        """
        tasks = self.repository.get_all()
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return {
            "success": True,
            "action": "tasks_listed",
            "tasks": [self._task_to_dict(t) for t in tasks],
            "count": len(tasks),
        }
    
    def update_task(self, task_id: int, title: Optional[str] = None, 
                   description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)
            
        Returns:
            Updated task or error
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "action": "update_failed",
            }
        
        update_data = {}
        if title:
            update_data["title"] = title
        if description:
            update_data["description"] = description
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        updated_task = self.repository.update(task)
        
        return {
            "success": True,
            "action": "task_updated",
            "task": self._task_to_dict(updated_task),
        }
    
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            Success or error message
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "action": "delete_failed",
            }
        
        self.repository.delete(task_id)
        
        return {
            "success": True,
            "action": "task_deleted",
            "task_id": task_id,
        }
    
    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID to complete
            
        Returns:
            Updated task or error
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "action": "complete_failed",
            }
        
        task.mark_complete()
        completed_task = self.repository.update(task)
        
        return {
            "success": True,
            "action": "task_completed",
            "task": self._task_to_dict(completed_task),
        }
    
    def summarize_tasks(self) -> Dict[str, Any]:
        """
        Get a summary of all tasks.
        
        Returns:
            Task summary statistics
        """
        all_tasks = self.repository.get_all()
        pending = [t for t in all_tasks if t.status == "pending"]
        completed = [t for t in all_tasks if t.status == "completed"]
        
        return {
            "success": True,
            "action": "tasks_summarized",
            "summary": {
                "total": len(all_tasks),
                "pending": len(pending),
                "completed": len(completed),
            },
            "pending_tasks": [self._task_to_dict(t) for t in pending[:5]],  # Top 5
            "completed_tasks": [self._task_to_dict(t) for t in completed[:5]],  # Top 5
        }
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
    
    def get_tool_definitions(self) -> Dict[str, Dict[str, str]]:
        """
        Get tool definitions for AI agent.
        
        Returns:
            Dictionary of tool names and descriptions
        """
        return {
            "create_task": "Create a new task with title and optional description",
            "list_tasks": "List all tasks or filter by status (pending/completed)",
            "update_task": "Update an existing task by ID",
            "delete_task": "Delete a task by ID",
            "complete_task": "Mark a task as completed by ID",
            "summarize_tasks": "Get a summary of all tasks with counts",
        }
