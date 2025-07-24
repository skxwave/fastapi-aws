from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/jwt/login")
async def jwt_login():
    pass
