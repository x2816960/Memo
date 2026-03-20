from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_size: int
    file_type: str
    mime_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    sort_order: int
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskSortUpdate(BaseModel):
    task_ids: List[int]


class TaskStats(BaseModel):
    total: int
    todo: int
    in_progress: int
    completed: int
    cancelled: int
    due_today: int
    overdue: int
