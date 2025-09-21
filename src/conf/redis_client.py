import redis.asyncio as redis_asyncio
import os

_redis_instance = None

async def get_redis():
    global _redis_instance
    if _redis_instance is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_instance = await redis_asyncio.from_url(redis_url, encoding="utf8", decode_responses=True)
    return _redis_instance

