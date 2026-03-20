from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import UserResponse
from app.services.user import get_users, toggle_user_status, reset_user_password, get_user_by_id
from app.services.task import get_task_stats
from app.utils.security import get_current_admin_user
from app.models.user import User
from app.utils.config import get_config, update_config, init_default_config

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return get_users(db)


@router.patch("/users/{user_id}")
async def change_user_status(
    user_id: int,
    enabled: bool,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return toggle_user_status(db, user_id, enabled)


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    new_password: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return reset_user_password(db, user_id, new_password)


@router.get("/stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    from app.models.user import User
    from app.models.task import Task, TaskStatus

    total_users = db.query(User).count()
    total_tasks = db.query(Task).filter(Task.is_deleted == False).count()

    all_tasks = db.query(Task).filter(Task.is_deleted == False).all()
    status_counts = {
        "todo": sum(1 for t in all_tasks if t.status == TaskStatus.TODO),
        "in_progress": sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS),
        "completed": sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED),
        "cancelled": sum(1 for t in all_tasks if t.status == TaskStatus.CANCELLED)
    }

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "status_counts": status_counts
    }


@router.get("/config")
async def get_system_config(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    init_default_config(db)

    return {
        "image_max_size": int(get_config(db, "image_max_size")),
        "video_max_size": int(get_config(db, "video_max_size")),
        "other_max_size": int(get_config(db, "other_max_size")),
        "max_attachments_per_task": int(get_config(db, "max_attachments_per_task"))
    }


@router.put("/config")
async def update_system_config(
    config_updates: dict,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    for key, value in config_updates.items():
        update_config(db, key, str(value))

    return {"message": "Configuration updated successfully"}
