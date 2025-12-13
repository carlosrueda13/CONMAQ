import json
import redis
from typing import Any, Optional
from app.core.config import settings

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    """
    Retrieve a value from the cache.
    """
    try:
        value = redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except redis.RedisError:
        return None

def set_cache(key: str, value: Any, ttl: int = 60) -> None:
    """
    Set a value in the cache with a TTL (Time To Live).
    """
    try:
        redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except redis.RedisError:
        pass

def invalidate_cache(pattern: str) -> None:
    """
    Invalidate cache keys matching a pattern.
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except redis.RedisError:
        pass
