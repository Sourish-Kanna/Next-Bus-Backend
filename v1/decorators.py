from functools import wraps
import asyncio
from fastapi import HTTPException, status
from v1.response_base import TokenRequest
import v1.firebase as firebase

def log_activity(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # print("Decorator: sync Function is being called")
        x = func(*args, **kwargs)
        # print(f"Decorator: Function returned {x}")
        return x

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # print("Decorator: async Function is being called")
        x = await func(*args, **kwargs)
        # print(f"Decorator: Function returned {x}")
        return x

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def verify_id_token(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract token_request from args or kwargs
        token_request = None
        for arg in args:
            if isinstance(arg, TokenRequest):
                token_request = arg
                break
        if not token_request:
            token_request = kwargs.get("token_request")
        if not token_request or not getattr(token_request, "id_token", None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing id_token"
            )
        try:
            firebase.verify_token(token_request.id_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid id_token"
            )
        return await func(*args, **kwargs)
    return wrapper
