from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate, TaskSortUpdate, TaskStats
from app.services.task import (
    get_tasks, get_task_by_id, create_task, update_task,
    delete_task, update_task_status, update_task_order, get_task_stats
)
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=dict)
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.task import TaskStatus, TaskPriority

    status_enum = TaskStatus(status) if status else None
    priority_enum = TaskPriority(priority) if priority else None

    skip = (page - 1) * page_size
    tasks, total = get_tasks(
        db, current_user.id, status_enum, priority_enum, search, skip, page_size
    )

    return {
        "tasks": [TaskResponse.model_validate(t) for t in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=TaskResponse)
async def create_new_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_task = create_task(
        db, current_user.id, task.title, task.description, task.priority, task.due_date
    )
    # Convert ORM model to Pydantic model for serialization
    return TaskResponse.model_validate(new_task)


@router.get("/stats", response_model=TaskStats)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_task_stats(db, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_single_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task_by_id(db, task_id, current_user.id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_single_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = task_update.model_dump(exclude_unset=True)
    task = update_task(db, task_id, current_user.id, **update_data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
async def delete_single_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delete_task(db, task_id, current_user.id)
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = update_task_status(db, task_id, current_user.id, status_update.status)
    return TaskResponse.model_validate(task)


@router.put("/sort")
async def sort_tasks(
    sort_update: TaskSortUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_task_order(db, current_user.id, sort_update.task_ids)
    return {"message": "Tasks reordered successfully"}
