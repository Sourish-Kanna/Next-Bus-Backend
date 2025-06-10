from google.cloud.firestore_v1 import ArrayUnion
from fastapi import APIRouter
from v1.common_decorators import log_activity, verify_id_token
import v1.common_response_base as response_base
import v1.base_firebase as firebase

routes_timming_router = APIRouter(prefix="/timings", tags=["Timings"])

@routes_timming_router.get("/")
def get_routes():
    """Get all available routes."""
    return {"message": "List of routes"}

# @routes_timming_router.post("/add")
# @verify_id_token
# @log_activity
