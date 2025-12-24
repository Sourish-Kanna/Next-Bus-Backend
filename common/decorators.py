from functools import wraps
from fastapi import HTTPException, status
import common.firebase as firebase
import logging
import inspect

logger = logging.getLogger(__name__)

def log_activity(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "token"}
        logger.info(f"Called {func.__name__} with args={args} kwargs={filtered_kwargs}")        
        result = func(*args, **kwargs)
        # logger.info(f"{func.__name__} returned {result}")
        return result

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "token"}
        logger.info(f"Called {func.__name__} with args={args} kwargs={filtered_kwargs}")
        result = await func(*args, **kwargs)
        # logger.info(f"{func.__name__} returned {result}")
        return result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def verify_id_token(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = extract_token_from_kwargs_or_header(args, kwargs)
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
        token = extract_token_from_kwargs_or_header(args, kwargs)
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

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def  is_authenticated(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = extract_token_from_kwargs_or_header(args, kwargs)
        detail = firebase.get_admin_details(token)
        if not detail or not detail.get("isLoggedIn",False):
            logger.error("Authentication failed: No user details found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No user details found"
            )
        return func(*args, **kwargs)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = extract_token_from_kwargs_or_header(args, kwargs)
        detail = firebase.get_admin_details(token)
        if not detail or not detail.get("isLoggedIn",False):
            logger.error("Authentication failed: No user details found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No user details found"
            )
        return await func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
    
def is_admin(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = extract_token_from_kwargs_or_header(args, kwargs)
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
        token = extract_token_from_kwargs_or_header(args, kwargs)
        detail = firebase.get_admin_details(token)
        if not detail.get("isAdmin", False):
            logger.error("Authorization failed: User is not an admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization failed: User is not an admin"
            )
        return await func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# Helper function to extract token from kwargs or request headers 
def extract_token_from_kwargs_or_header(args, kwargs):
    # Try to get token from kwargs (FastAPI injects dependencies as kwargs)
    token = kwargs.get("token")
    if token:
        return token
    # Try to get token from request headers if available
    for arg in args:
        if hasattr(arg, "headers"):
            auth_header = arg.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header.split(" ", 1)[1]
    logger.error("Missing or invalid Authorization header")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid Authorization header"
    )
