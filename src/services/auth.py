from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import os
import json

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.database.models import User
from fastapi.security import OAuth2PasswordBearer
from src.conf.redis_client import get_redis

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authentication.

    Args:
        data (dict): Data to encode in the token.
        expires_delta (Optional[timedelta]): Expiration time delta.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode a JWT access token.

    Args:
        token (str): JWT token to decode.

    Returns:
        Optional[dict]: Decoded payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login")),
                           db: AsyncSession = Depends(get_db)) -> User:
    """
    Retrieve the current authenticated user from the JWT token.

    Args:
        token (str): JWT token from request.
        db (AsyncSession): Database session dependency.

    Returns:
        User: Authenticated user instance.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = int(payload.get("sub"))
    redis = await get_redis()
    cache_key = f"user:{user_id}"
    cached_user = await redis.get(cache_key)
    if cached_user:
        user_dict = json.loads(cached_user)
        return User(**user_dict)
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    user_dict = {
        "id": db_user.id,
        "email": db_user.email,
        "hashed_password": db_user.hashed_password,
        "is_active": db_user.is_active,
        "avatar": db_user.avatar,
        "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
        "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None,
        "is_verified": db_user.is_verified,
        "verification_token": db_user.verification_token,
        "role": db_user.role,
    }
    await redis.set(cache_key, json.dumps(user_dict), ex=3600)
    return db_user
