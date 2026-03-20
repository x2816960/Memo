from datetime import datetime, date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.task import Task, TaskPriority, TaskStatus
from app.models.attachment import Attachment, AttachmentType


# Valid status transitions
VALID_TRANSITIONS = {
    TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.TODO],
    TaskStatus.COMPLETED: [],
    TaskStatus.CANCELLED: [TaskStatus.TODO]
}


def get_tasks(
    db: Session,
    user_id: int,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Task], int]:
    query = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Task.title.like(search_pattern)) | (Task.description.like(search_pattern))
        )

    total = query.count()
    tasks = query.order_by(Task.sort_order.asc(), Task.created_at.desc()).offset(skip).limit(limit).all()

    return tasks, total


def get_task_by_id(db: Session, task_id: int, user_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


def create_task(db: Session, user_id: int, title: str, description: str = None,
                priority: TaskPriority = TaskPriority.MEDIUM, due_date: datetime = None) -> Task:
    # Get max sort_order for user
    max_order = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False).count()

    task = Task(
        title=title,
        description=description,
        priority=priority,
        status=TaskStatus.TODO,
        due_date=due_date,
        sort_order=max_order,
        user_id=user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, user_id: int, **kwargs) -> Task:
    task = get_task_by_id(db, task_id, user_id)

    for key, value in kwargs.items():
        if value is not None and hasattr(task, key):
            setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int):
    task = get_task_by_id(db, task_id, user_id)
    task.is_deleted = True
    db.commit()


def update_task_status(db: Session, task_id: int, user_id: int, new_status: TaskStatus) -> Task:
    task = get_task_by_id(db, task_id, user_id)

    if new_status not in VALID_TRANSITIONS.get(task.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {task.status.value} to {new_status.value}"
        )

    task.status = new_status
    db.commit()
    db.refresh(task)
    return task


def update_task_order(db: Session, user_id: int, task_ids: List[int]):
    for idx, task_id in enumerate(task_ids):
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False).first()
        if task:
            task.sort_order = idx
    db.commit()


def get_task_stats(db: Session, user_id: int) -> dict:
    tasks = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False)
    all_tasks = tasks.all()

    total = len(all_tasks)
    todo = sum(1 for t in all_tasks if t.status == TaskStatus.TODO)
    in_progress = sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS)
    completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
    cancelled = sum(1 for t in all_tasks if t.status == TaskStatus.CANCELLED)

    today = datetime.utcnow().date()
    due_today = sum(1 for t in all_tasks
                    if t.due_date and t.due_date.date() == today and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED])
    overdue = sum(1 for t in all_tasks
                   if t.due_date and t.due_date.date() < today and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED])

    return {
        "total": total,
        "todo": todo,
        "in_progress": in_progress,
        "completed": completed,
        "cancelled": cancelled,
        "due_today": due_today,
        "overdue": overdue
    }


def add_attachment(db: Session, task_id: int, user_id: int, file_name: str, file_path: str,
                   file_size: int, file_type: AttachmentType, mime_type: str) -> Attachment:
    task = get_task_by_id(db, task_id, user_id)

    # Check max attachments limit
    existing_count = db.query(Attachment).filter(Attachment.task_id == task_id).count()
    if existing_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum attachments per task (10) reached"
        )

    attachment = Attachment(
        task_id=task_id,
        file_name=file_name,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        mime_type=mime_type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get_attachments(db: Session, task_id: int, user_id: int) -> List[Attachment]:
    task = get_task_by_id(db, task_id, user_id)
    return db.query(Attachment).filter(Attachment.task_id == task_id).all()


def delete_attachment(db: Session, attachment_id: int, user_id: int):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # Verify user owns the task
    task = get_task_by_id(db, attachment.task_id, user_id)

    db.delete(attachment)
    db.commit()
