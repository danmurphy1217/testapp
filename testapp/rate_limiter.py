from functools import wraps
from typing import Callable, TypeVar, Any
from fastapi import HTTPException, Request
from testapp.redis import Redis, constants

redis_client = Redis(namespace=constants.Namespace.RATE_LIMIT)
FuncT = TypeVar("FuncT", bound=Callable[..., Any])

# Rate limit decorator using Redis
def rate_limit(limit: int, period: int):
    """
    Naive rate limit decorator using Redis. Does not account for a rolling window.
    
    TODO: Implement a rolling window rate limit, or a more sophisticated algorithm.
    """
    def decorator(func: FuncT):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TODO: use IP address for key
            key = "rate_limit"

            # Get the current count or set to 0 if it doesn't exist
            current_count = redis_client.get(key)
            if current_count is None:
                # Use setex to atomically set value with expiry
                redis_client.setex(key, period, 1)
                current_count = 1
            else:
                current_count = int(current_count) # type: ignore
                if current_count >= limit:
                    raise HTTPException(status_code=429, detail="Too many requests")
                # Increment only if we haven't hit the limit
                current_count = redis_client.incr(key)

            return await func(*args, **kwargs)
        return wrapper
    return decorator