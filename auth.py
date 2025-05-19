from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/login")
async def login():
    return {"message": "Login successful"}

@auth_router.post("/register")
async def register():
    return {"message": "Registration successful"}