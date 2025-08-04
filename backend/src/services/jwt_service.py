from typing import Optional
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status

from src.core.config import get_env
from src.db.models import User, Web3User
from src.schemas.auth import TokenPair

config = get_env()


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
