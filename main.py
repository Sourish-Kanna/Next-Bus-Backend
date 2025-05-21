from fastapi import FastAPI, APIRouter
from v1 import auth,test,firebase

app = FastAPI()
# Including the root endpoint
@app.get('/')
def root():
    return {"message": "Welcome to the API!"}

'''Version 1'''
# Importing routers from v1 module
ver_1 = APIRouter(prefix="/v1")
ver_1.include_router(auth.auth_router)
ver_1.include_router(test.test_router)
ver_1.include_router(firebase.firebase_router)

# Including the root endpoint for version 1
@ver_1.get('/')
def hello():
    return {"message": "Welcome to the API V1!"}



# Including the version 1 router in the main app
app.include_router(ver_1)