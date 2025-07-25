from typing import Optional
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from src.core.config import get_env
from src.db.models import User
from src.schemas.auth import TokenPair

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


def create_token_pair(user: User) -> TokenPair:
    access_token_payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "type": "access",
    }
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
