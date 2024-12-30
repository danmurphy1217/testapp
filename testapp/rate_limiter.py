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
            request: Request = args[0]  # first argument should be the request
            client_ip = request.client.host 
            key = f"rate_limit:{client_ip}"

            # Get the current count or set to 0 if it doesn't exist
            current_count = redis_client.get(key)
            if current_count is None:
                # Use setex to atomically set value with expiry
                success = redis_client.setex(key, period, 1)
                current_count = 1 if success is None else 0
            else:
                current_count = int(current_count)
                if current_count >= limit:
                    raise HTTPException(status_code=429, detail="Too many requests")
                # Increment only if we haven't hit the limit
                current_count = redis_client.incr(key)

            return await func(*args, **kwargs)
        return wrapper
    return decorator