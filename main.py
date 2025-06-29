from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import v1
import logging
import v1.common.firebase as firebase
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("Firebase initializing at startup.")
firebase.initialize_firebase()
logger.info("Firebase initialized at startup.")

app = FastAPI()


# Configure CORS
if os.getenv("ENABLE_TEST_ROUTE", "false").lower() == "true":
    logger.info("Loading Dev env....")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.info("Loading Production env....")
    origin_list = [
    "https://next-bus-app.netlify.app",
    "https://next-bus-dev.netlify.app/"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Including the root endpoint
@app.get('/')
def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the API!"}

# Including the version 1 router in the main app
app.include_router(v1.ver_1)