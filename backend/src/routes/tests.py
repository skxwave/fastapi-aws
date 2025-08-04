import asyncio

from redis.asyncio import Redis
from fastapi import APIRouter

from src.core.config import get_env

router = APIRouter(prefix="/tests", tags=["Tests"])
config = get_env()
redis = Redis(
    host=config.redis.url,
    port=6379,
    decode_responses=True,
)


@router.get("/no-cache")
async def no_cache():
    await asyncio.sleep(2)
    return {"cached": False, "data": "expensive result"}


@router.get("/with-cache")
async def with_cache():
    cache_key = "expensive_result"
    cached = await redis.get(cache_key)

    if cached:
        return {"cached": True, "data": cached}

    await asyncio.sleep(2)
    result = "expensive result"
    await redis.set(cache_key, result, ex=60)

    return {"cached": False, "data": result}
