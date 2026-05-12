from fastapi import FastAPI, Request, Response, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import common.firebase as firebase
import logging
from common.config import load_env, resolve_origins, get_env

# Load dev env only when DEV_ENV=true
load_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(message)s"
)
logger = logging.getLogger(__name__)

# --- Firebase initialization moved into the lifespan event ---

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Validate critical environment variables before starting the app
    logger.info("Validating environment...")
    get_env("ORIGIN_LIST", required=True)

    # Initialize Firebase
    logger.info("Firebase initializing at startup.")
    firebase.initialize_firebase()
    logger.info("Firebase initialized at startup.")
    
    yield  # The application runs here
    
    # Graceful shutdown logic
    if firebase.firebase_app:
        import firebase_admin
        firebase_admin.delete_app(firebase.firebase_app)
    
    logger.info("Application is shutting down.")
    logging.shutdown() # Ensure all logs are flushed to Render/Console

# --- Tags Metadata ---
tags_metadata = [
    {
        "name": "Routes",
        "description": "Public and Admin endpoints for managing bus route metadata.",
    },
    {
        "name": "Timings",
        "description": "Core engine for crowdsourced bus timings. Includes **Auto-Aggregation** logic and threshold matching.",
    },
    {
        "name": "User",
        "description": "Firebase authentication sync and role-based access details.",
    },
    {
        "name": "Future (ML/Historical)",
        "description": "Endpoints and background logic designed for saving historical delay data for future AI model training.",
    },
    {
        "name": "Test",
        "description": "Diagnostic tools available only in `DEV_ENV`. Includes token verification helpers.",
    },
]

# --- Pass the lifespan function to your app ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan, title="NextBus Backend", version="2.1.7", openapi_tags=tags_metadata)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore

if get_env("DEV_ENV", "false") == "true": logger.info("Loading Dev env....") 
else: logger.info("Loading Production env....")

origin_list = resolve_origins()
logger.info(f"Allowed origins: {origin_list}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including the root endpoint
@app.head("/",  response_model=None)
@app.get("/",  response_model=None)
def root(request: Request):
    if request.method == "HEAD":
        logger.info("Root endpoint called with HEAD request")
        return Response(status_code=status.HTTP_200_OK)
    else:
        logger.info("Root endpoint called with GET request")
        return {
            "message": "Welcome to the API!", 
            "version": "2.1.7",
            "dev_env": get_env("DEV_ENV", "false") == "true"
            }

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)

import v1
app.include_router(v1.ver_1)