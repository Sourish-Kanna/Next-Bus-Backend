from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/login")
async def login() -> dict[str, str]:
    """Simulate a login endpoint."""
    return {"message": "Login successful"}

@auth_router.post("/register")
async def register() -> dict[str, str]:
    """Simulate a registration endpoint."""
    return {"message": "Registration successful"}