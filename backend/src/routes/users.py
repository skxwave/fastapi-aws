from typing import Union
from fastapi import APIRouter, Depends

from src.schemas.user import UserRead, Web3UserRead
from src.db.models.user import User, Web3User
from src.core.config import get_env
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
config = get_env()


@router.get("/me", response_model=Union[UserRead, Web3UserRead])
async def my_profile(user: User | Web3User = Depends(get_current_user)):
    if isinstance(user, User):
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
        }
    return {
        "id": str(user.id),
        "wallet": user.wallet_address,
    }
