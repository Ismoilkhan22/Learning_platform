"""
# Redis ulanish sozlamalari
"""
from redis import Redis

import os

async def get_redis():
    redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    try:
        yield redis
    finally:
        await redis.close()