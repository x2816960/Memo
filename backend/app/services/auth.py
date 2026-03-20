from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole, UserStatus
from app.utils.security import get_password_hash, verify_password, create_access_token, REMEMBER_ME_EXPIRE_DAYS


LOCKOUT_DURATION = timedelta(minutes=15)
MAX_FAILED_ATTEMPTS = 5


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked. Try again after {(user.locked_until - datetime.utcnow()).seconds // 60} minutes"
        )

    if not verify_password(password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
            user.failed_login_attempts = 0
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Reset failed attempts on successful login
    if user.failed_login_attempts > 0 or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    return user


def create_user_token(user: User, remember_me: bool = False) -> str:
    expire_minutes = REMEMBER_ME_EXPIRE_DAYS * 24 * 60 if remember_me else 24 * 60
    expires_delta = timedelta(minutes=expire_minutes)
    return create_access_token(
        data={"sub": user.id},
        expires_delta=expires_delta
    )


def register_user(db: Session, username: str, password: str, email: str = None, nickname: str = None) -> User:
    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        username=username,
        email=email,
        nickname=nickname or username,
        hashed_password=get_password_hash(password),
        role=UserRole.USER,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def init_admin_user(db: Session):
    """Initialize default admin user if not exists"""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email=None,
            nickname="Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            must_change_password=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin
