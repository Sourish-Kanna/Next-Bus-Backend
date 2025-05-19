from fastapi import FastAPI, APIRouter
from auth import auth_router
from test import test_router
from firebase import firebase_router

app = FastAPI()

ver_1 = APIRouter(prefix="/v1")
ver_1.include_router(auth_router)
ver_1.include_router(test_router)
ver_1.include_router(firebase_router)
@ver_1.get('/')
def hello():
    return {"message": "Welcome to the API!"}

app.include_router(ver_1)

@app.get('/')
def root():
    return {"message": "Welcome to the API!"}