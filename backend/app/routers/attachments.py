import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.task import AttachmentResponse
from app.services.task import get_attachments, delete_attachment, add_attachment
from app.utils.security import get_current_user
from app.models.user import User
from app.models.attachment import AttachmentType
from app.utils.config import get_config

router = APIRouter(prefix="/api", tags=["attachments"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/quicktime", "video/x-matroska"}
ALLOWED_OTHER_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "application/zip",
    "application/x-rar-compressed"
}


def ensure_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


def get_file_type(mime_type: str) -> AttachmentType:
    if mime_type in ALLOWED_IMAGE_TYPES:
        return AttachmentType.IMAGE
    elif mime_type in ALLOWED_VIDEO_TYPES:
        return AttachmentType.VIDEO
    else:
        return AttachmentType.OTHER


def get_max_size(file_type: AttachmentType, db: Session) -> int:
    if file_type == AttachmentType.IMAGE:
        return int(get_config(db, "image_max_size"))
    elif file_type == AttachmentType.VIDEO:
        return int(get_config(db, "video_max_size"))
    else:
        return int(get_config(db, "other_max_size"))


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentResponse)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ensure_upload_dir()

    # Get task to verify ownership
    from app.services.task import get_task_by_id
    get_task_by_id(db, task_id, current_user.id)

    # Determine file type
    mime_type = file.content_type or "application/octet-stream"
    file_type = get_file_type(mime_type)

    # Check file size
    max_size = get_max_size(file_type, db)

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed ({max_size // (1024*1024)}MB) for {file_type.value}"
        )

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    attachment = add_attachment(
        db, task_id, current_user.id,
        file.filename, file_path, file_size, file_type, mime_type
    )

    return attachment


@router.get("/tasks/{task_id}/attachments", response_model=List[AttachmentResponse])
async def list_attachments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_attachments(db, task_id, current_user.id)


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Verify ownership
    from app.services.task import get_task_by_id
    get_task_by_id(db, attachment.task_id, current_user.id)

    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        attachment.file_path,
        media_type=attachment.mime_type,
        filename=attachment.file_name
    )


@router.delete("/attachments/{attachment_id}")
async def remove_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Delete physical file
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    delete_attachment(db, attachment_id, current_user.id)
    return {"message": "Attachment deleted successfully"}
