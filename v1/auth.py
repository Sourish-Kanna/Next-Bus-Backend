from fastapi import APIRouter
from .cust_logging import log_activity

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/login")
@log_activity
async def login() -> dict[str, str]:
    """Simulate a login endpoint."""
    return {"message": "Login successful"}

@auth_router.post("/register")
@log_activity
def register() -> dict[str, str]:
    """Simulate a registration endpoint."""
    return {"message": "Registration successful"}