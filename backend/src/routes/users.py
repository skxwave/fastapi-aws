from fastapi import APIRouter

from src.core.config import get_env

router = APIRouter(prefix="/users", tags=["Users"])
config = get_env()


@router.get("/me")
async def my_profile():
    return {
        "host": config.db.host,
        "port": config.db.port,
        "name": config.db.name,
        "user": config.db.user,
        "password": config.db.password,
        "url": config.db.url,
    }
    # return {
    #     "username": "Test User",
    #     "email": "user@example.com",
    # }
