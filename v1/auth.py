from fastapi import APIRouter
import v1

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/login")
@v1.log_activity
async def login() -> dict[str, str]:
    """Simulate a login endpoint."""
    return {"message": "Login successful"}

@auth_router.post("/register")
@v1.log_activity
def register() -> dict[str, str]:
    """Simulate a registration endpoint."""
    return {"message": "Registration successful"}