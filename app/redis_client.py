from redis.asyncio import Redis
import os

def get_redis():
    redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    try:
        yield redis
    finally:
        redis.close()