from fastapi import APIRouter, Depends

from src.schemas.user import UserRead
from src.db.models.user import User
from src.core.config import get_env
from src.db.repositories import user_repo

router = APIRouter(prefix="/users", tags=["Users"])
config = get_env()


@router.get("/me", response_model=UserRead)
async def my_profile(user: User = Depends(user_repo.get_current_user)):
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
    }
