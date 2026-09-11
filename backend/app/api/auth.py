from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token({"sub": str(user.id)}))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
