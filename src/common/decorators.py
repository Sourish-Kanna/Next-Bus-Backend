from functools import wraps
from fastapi import HTTPException, status
import common.firebase as firebase
import logging
import inspect

logger = logging.getLogger(__name__)

def log_activity(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Filter out token or credentials from logs for security
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["token", "credentials"]}
        logger.info(f"Called {func.__name__} with args={args} kwargs={filtered_kwargs}")        
        result = func(*args, **kwargs)
        return result

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["token", "credentials"]}
        logger.info(f"Called {func.__name__} with args={args} kwargs={filtered_kwargs}")
        result = await func(*args, **kwargs)
        return result

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

def verify_id_token(func):
    """
    Decorator that expects a 'token' string keyword argument 
    already injected by Depends(firebase.get_user_token).
    """
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        try:
            firebase.verify_token(token)
            logger.info("Token verified in decorator.")
        except Exception as e:
            logger.error(f"Token verification failed in decorator: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {e}"
            )
        return func(*args, **kwargs)
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        try:
            firebase.verify_token(token)
            logger.info("Token verified in decorator.")
        except Exception as e:
            logger.error(f"Token verification failed in decorator: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {e}"
            )
        return await func(*args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

def is_authenticated(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        detail = firebase.get_admin_details(token)
        if not detail or not detail.get("isLoggedIn", False):
            logger.error("Authentication failed: No user details found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No user details found"
            )
        return func(*args, **kwargs)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        detail = firebase.get_admin_details(token)
        if not detail or not detail.get("isLoggedIn", False):
            logger.error("Authentication failed: No user details found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No user details found"
            )
        return await func(*args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    
def is_admin(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        detail = firebase.get_admin_details(token)
        if not detail.get("isAdmin", False):
            logger.error("Authorization failed: User is not an admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization failed: User is not an admin"
            )
        return func(*args, **kwargs)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = kwargs.get("token")
        detail = firebase.get_admin_details(token)
        if not detail.get("isAdmin", False):
            logger.error("Authorization failed: User is not an admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization failed: User is not an admin"
            )
        return await func(*args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper