from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserStatus
from app.utils.security import get_password_hash


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def toggle_user_status(db: Session, user_id: int, enabled: bool) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.status = UserStatus.ACTIVE if enabled else UserStatus.DISABLED
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: int, new_password: str) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.hashed_password = get_password_hash(new_password)
    user.must_change_password = True
    db.commit()
    db.refresh(user)
    return user
