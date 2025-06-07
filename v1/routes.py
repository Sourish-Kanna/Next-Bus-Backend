from fastapi import APIRouter, Body
from v1.common_decorators import log_activity, verify_id_token
from v1.common_response_base import FireBaseResponse, TokenRequest
import v1.base_firebase as firebase

routes_router = APIRouter(prefix="/routes", tags=["Routes"])

@routes_router.get("/")
def get_routes():
    """Get all available routes."""
    return {"message": "List of routes"}
