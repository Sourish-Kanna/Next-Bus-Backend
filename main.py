from fastapi import FastAPI
import v1

app = FastAPI()
# Including the root endpoint
@app.get('/')
def root():
    return {"message": "Welcome to the API!"}

# Including the version 1 router in the main app
app.include_router(v1.ver_1)