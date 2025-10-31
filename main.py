from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import v1.common.firebase as firebase
import v1
import logging
import os
import dotenv

dotenv.load_dotenv()

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

if os.getenv("DEV_ENV", "false").lower() == "true":
    logger.info("Loading Dev env....")
else:
    logger.info("Loading Production env....")

origin_list_str = os.getenv("ORIGIN_LIST")
if origin_list_str == "*":
    origin_list = ["*"]
else:
    origin_list = origin_list_str.split(",") if origin_list_str else []
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
        return Response(status_code=200)
    else:
        logger.info("Root endpoint called with GET request")
        return {"message": "Welcome to the API!"}

# Silent favicon handler (no 404, no docs entry)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)  # 204 = No Content

# Including the version 1 router in the main app
app.include_router(v1.ver_1)