from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User, Profile
from app.auth import (
    get_current_user,
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if "@" not in data.email or "." not in data.email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email format")

    existing = db.execute(select(User).where(User.email == data.email.lower().strip())).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=data.email.lower().strip(),
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id, email=user.email)
    db.add(profile)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == data.email.lower().strip())).scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.put("/me")
def update_password(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user.hashed_password = get_password_hash(data.password)
    db.commit()
    return {"ok": True}


@router.get("/token-info")
def token_info(user: User = Depends(get_current_user)):
    return {
        "user_id": user.id,
        "email": user.email,
        "token_expires_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
    }
