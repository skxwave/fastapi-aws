from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserCreate
from src.schemas.auth import LoginRequest, TokenPair
from src.db.session import get_async_session
from src.services.auth import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/jwt/register", response_model=TokenPair)
async def register(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        return await register_user(user_create, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/jwt/login", response_model=TokenPair)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        return await authenticate_user(data.identifier, data.password, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
