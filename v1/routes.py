from fastapi import APIRouter, Body
from v1.decorators import log_activity, verify_id_token
from v1.response_base import FireBaseResponse, TokenRequest
import v1.firebase as firebase

routes_router = APIRouter(prefix="/routes", tags=["Firebase"])

