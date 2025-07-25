from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models import User
from src.db.session import get_async_session
from src.schemas.user import UserCreate
from src.services.auth import (
    create_token_pair,
    decode_access_token,
    hash_password,
    verify_password,
)

http_bearer = HTTPBearer()


class UserRepository:
    async def register_user(
        self,
        user_create: UserCreate,
        session: AsyncSession,
    ) -> User:
        existing_user = await session.scalar(
            select(User).where(
                (User.email == user_create.email)
                | (User.username == user_create.username)
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
        self,
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
        self,
        session: AsyncSession = Depends(get_async_session),
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token missing subject",
            )
        user = await session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user


user_repo = UserRepository()
