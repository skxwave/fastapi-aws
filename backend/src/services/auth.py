import secrets
import string
from typing import Optional
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eth_account import Account
from eth_account.messages import encode_defunct

from src.core.config import get_env
from src.db.models import User, Web3User
from src.db.session import get_async_session
from src.schemas.auth import TokenPair

http_bearer = HTTPBearer()
config = get_env()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_token_pair(user: User | Web3User) -> TokenPair:
    access_token_payload = {
        "sub": str(user.id),
        "type": "access",
    }

    if isinstance(user, User):
        access_token_payload["username"] = user.username
        access_token_payload["email"] = user.email
        access_token_payload["user_type"] = "default"
    elif isinstance(user, Web3User):
        access_token_payload["wallet"] = user.wallet_address
        access_token_payload["user_type"] = "web3"

    refresh_token_payload = {
        "sub": str(user.id),
        "type": "refresh",
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
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def create_nonce(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def verify_signature(
    signature: str,
    expected_address: str,
    session: AsyncSession,
) -> bool:
    user = await session.scalar(
        select(Web3User).where(Web3User.wallet_address == expected_address)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    try:
        # EIP-191 encoding
        encoded_message = encode_defunct(text=user.nonce)
        recovered_address = Account.recover_message(
            encoded_message,
            signature=signature,
        )
        # Compare lowercase to avoid checksum issues
        if recovered_address.lower() == expected_address.lower():
            return create_token_pair(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )


async def get_current_user(
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
    user_type = payload.get("user_type")
    if user_type == "default":
        user = await session.scalar(select(User).where(User.id == user_id))
    elif user_type == "web3":
        user = await session.scalar(
            select(Web3User).where(Web3User.wallet_address == payload.get("wallet"))
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
