from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from passlib.context import CryptContext

from app.database import get_db
from app.models import User

router = APIRouter(prefix="", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    login: str
    password: str

class UserCheck(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    id: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.login == payload.login))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Login already taken")
    user = User(
        login=payload.login,
        hashed_password=pwd_context.hash(payload.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id), "login": user.login}

@router.post("/check")
async def check_user(payload: UserCheck, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.login == payload.login))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserResponse(id=str(user.id))