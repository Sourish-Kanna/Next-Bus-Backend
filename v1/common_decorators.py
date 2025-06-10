from functools import wraps
import asyncio
from fastapi import HTTPException, status
import v1.base_firebase as firebase

def log_activity(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        x = func(*args, **kwargs)
        return x

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        x = await func(*args, **kwargs)
        return x

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def verify_id_token(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = None
        token = kwargs.get("input").token  # type: ignore
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing id_token"
            )
        try:
            firebase.verify_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {e}"
            )
        return func(*args, **kwargs)
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = None
        token = kwargs.get("input").token # type: ignore
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing id_token"
            )
        try:
            firebase.verify_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {e}"
            )
        return await func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
