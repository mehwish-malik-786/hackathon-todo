from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from repositories.task_repository import TaskRepository
from database import get_session

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_repository(session: Session = Depends(get_session)) -> TaskRepository:
    """Get task repository instance."""
    return TaskRepository(session)


@router.get("", response_model=List[TaskResponse])
def list_tasks(repo: TaskRepository = Depends(get_repository)):
    """
    Get all tasks.
    
    Returns:
        List of all tasks ordered by creation date
    """
    return repo.get_all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate, repo: TaskRepository = Depends(get_repository)
):
    """
    Create a new task.
    
    Args:
        task_data: Task creation data (title, description)
        
    Returns:
        Created task with ID and timestamps
    """
    task = Task(**task_data.model_dump())
    return repo.add(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    """
    Get task by ID.
    
    Args:
        task_id: Task unique identifier
        
    Returns:
        Task if found
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repo: TaskRepository = Depends(get_repository),
):
    """
    Update an existing task.
    
    Args:
        task_id: Task unique identifier
        task_data: Fields to update (title, description)
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    return repo.update(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    """
    Delete a task.
    
    Args:
        task_id: Task unique identifier
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    repo.delete(task_id)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    """
    Mark task as completed.
    
    Args:
        task_id: Task unique identifier
        
    Returns:
        Updated task with completed status and timestamp
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    task.mark_complete()
    return repo.update(task)
