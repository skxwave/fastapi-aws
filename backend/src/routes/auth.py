from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import create_nonce, verify_signature
from src.schemas.user import UserCreate
from src.schemas.auth import (
    LoginRequest,
    Nonce,
    TokenPair,
    Web3LoginRequest,
    Web3NonceRequest,
)
from src.db.session import get_async_session
from src.db.repositories import user_repo

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/jwt/register", response_model=TokenPair)
async def jwt_register(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        return await user_repo.register_user(user_create, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/jwt/login", response_model=TokenPair)
async def jwt_login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        return await user_repo.authenticate_user(
            data.identifier,
            data.password,
            session,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/web3/get_nonce", response_model=Nonce)
async def web3_get_nonce(
    data: Web3NonceRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await user_repo.get_and_save_nonce(data, session)


@router.post("/web3/login", response_model=TokenPair)
async def web3_login(
    data: Web3LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    return await verify_signature(
        signature=data.signature,
        expected_address=data.address,
        session=session,
    )
