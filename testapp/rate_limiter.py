from functools import wraps
from typing import Callable, TypeVar, Any, cast
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
        async def wrapper(request: Request, *args, **kwargs):
            assert request.client is not None
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"

            # Get the current count or set to 0 if it doesn't exist
            current_count: int = cast(int, redis_client.get(key, default=0))
            if current_count == 0:
                # atomically set value with expiration
                redis_client.setex(key, period, 1)
            else:
                if current_count >= limit:
                    raise HTTPException(status_code=429, detail="Too many requests")
                # increment the count if we haven't hit the limit
                redis_client.incr(key)

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 