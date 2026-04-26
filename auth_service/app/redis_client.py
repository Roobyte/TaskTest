import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}",
    decode_responses=True
)