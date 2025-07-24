from fastapi import APIRouter, Depends

from src.schemas.user import UserRead
from src.db.models.user import User
from src.core.config import get_env
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
config = get_env()


@router.get("/me", response_model=UserRead)
async def my_profile(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
    }
