from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.config import get_env
from src.db.models import User
from src.db.session import get_async_session
from src.schemas.user import UserCreate
from src.schemas.auth import TokenPair

config = get_env()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.jwt.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        payload=to_encode,
        key=config.jwt.secret_key,
        algorithm=config.jwt.algorithm,
    )


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=config.jwt.refresh_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        payload=to_encode,
        key=config.jwt.secret_key,
        algorithm=config.jwt.algorithm,
    )


def create_token_pair(user: User) -> TokenPair:
    access_token_payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "type": "access"
    }
    refresh_token_payload = {
        "sub": str(user.id),
        "type": "refresh"
    }
    return TokenPair(
        access_token=create_access_token(access_token_payload),
        refresh_token=create_refresh_token(refresh_token_payload),
        token_type="bearer",
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            jwt=token,
            key=config.jwt.secret_key,
            algorithms=[config.jwt.algorithm],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token type",
            )
        return payload
    except PyJWTError:
        return None


async def register_user(
    user_create: UserCreate,
    session: AsyncSession,
) -> User:
    existing_user = await session.scalar(
        select(User).where(
            (User.email == user_create.email) | (User.username == user_create.username)
        )
    )
    if existing_user:
        raise ValueError("User with this email or username already exists")

    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return create_token_pair(user)


async def authenticate_user(
    identifier: str,
    password: str,
    session: AsyncSession,
) -> User | None:
    user = await session.scalar(
        select(User).where(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )
    )

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    return create_token_pair(user)


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found",
        )

    return await session.scalar(select(User).where(User.id == user_id))
