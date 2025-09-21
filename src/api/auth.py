import uuid

from cloudinary.uploader import upload as cloudinary_upload
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi_limiter.depends import RateLimiter
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.conf.redis_client import get_redis
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from src.services.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user in the system.

    Args:
        user (UserCreate): User registration data.
        db (AsyncSession): Database session dependency.

    Returns:
        UserResponse: Registered user data.

    Raises:
        HTTPException: If user already exists (409).
    """
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = pwd_context.hash(user.password)
    verification_token = str(uuid.uuid4())
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=verification_token,
        role='user'  # Set default role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    # log the verif link to mock email sending
    print(f"[DEBUG] Email verification link: http://localhost:8000/auth/verify-email?token={verification_token}")
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        is_active=new_user.is_active,
        avatar=new_user.avatar,
        created_at=new_user.created_at,
        is_verified=new_user.is_verified,
        role=new_user.role  # Pass role to response
    )

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify user's email using a token.

    Args:
        token (str): Verification token from email link.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If token is invalid or expired (400).
    """
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user.is_verified = True
    user.verification_token = None
    await db.commit()
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT access token.

    Args:
        user (UserLogin): Login credentials.
        db (AsyncSession): Database session dependency.

    Returns:
        TokenResponse: JWT access token.

    Raises:
        HTTPException: If credentials are invalid (401).
    """
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Args:
        current_user (User): Current authenticated user dependency.

    Returns:
        UserResponse: User profile data.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        is_verified=current_user.is_verified
    )

@user_router.post("/avatar", status_code=201)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's avatar image using Cloudinary.

    Args:
        file (UploadFile): Uploaded avatar image file.
        current_user (User): Current authenticated user dependency.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Avatar URL.

    Raises:
        HTTPException: If upload fails or server error occurs.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can change their avatar themselves.")
    try:
        result = cloudinary_upload(file.file, folder="avatars")
        avatar_url = result.get("secure_url")
        if not avatar_url:
            raise HTTPException(status_code=400, detail="Error uploading file to Cloudinary")
        current_user.avatar = avatar_url
        await db.commit()
        await db.refresh(current_user)
        return {"avatar": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(email: str = Body(..., embed=True)):
    """
    Request password reset. Generates a token, saves it in Redis, and logs email sending (mock).
    """
    redis = await get_redis()
    token = str(uuid.uuid4())
    await redis.set(f"reset:{token}", email, ex=3600)  # Token valid for 1 hour
    # Here you can send email, but for testing just log
    print(f"[MOCK EMAIL] To reset your password, go to: /auth/reset-password?token={token}")
    return {"msg": "Password reset instructions sent to email (mock)"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(token: str = Body(...), new_password: str = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Reset password by token. Checks token, updates user's password.
    """
    redis = await get_redis()
    email = await redis.get(f"reset:{token}")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    await db.refresh(user)
    await redis.delete(f"reset:{token}")
    return {"msg": "Password successfully reset"}
