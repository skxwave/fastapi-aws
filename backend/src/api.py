from fastapi import APIRouter
from .routes import users_router, auth_router, tests_router

api_router = APIRouter(prefix="/api")

api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(tests_router)
