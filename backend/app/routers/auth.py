from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest
from app.schemas.user import UserResponse, PasswordChange
from app.services.auth import authenticate_user, create_user_token, register_user
from app.utils.security import get_current_user, verify_password, get_password_hash
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(
        db,
        username=req.username,
        password=req.password,
        email=req.email,
        nickname=req.nickname
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    token = create_user_token(user, req.remember_me)
    return TokenResponse(access_token=token)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.hashed_password = get_password_hash(password_change.new_password)
    current_user.must_change_password = False
    db.commit()

    return {"message": "Password changed successfully"}


@router.put("/password/admin")
async def admin_change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Force password change for must_change_password users
    if current_user.must_change_password:
        current_user.hashed_password = get_password_hash(password_change.new_password)
        current_user.must_change_password = False
        db.commit()
        return {"message": "Password changed successfully"}

    # Normal password change requires old password
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
