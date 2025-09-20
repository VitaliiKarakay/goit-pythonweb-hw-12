from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserCreate, UserResponse, UserLogin
from passlib.context import CryptContext
from sqlalchemy.future import select

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        is_active=new_user.is_active,
        avatar=new_user.avatar,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        avatar=db_user.avatar,
        created_at=db_user.created_at
    )
