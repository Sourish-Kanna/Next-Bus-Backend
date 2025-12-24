from fastapi import APIRouter, Body, HTTPException , status, Depends
from google.api_core.exceptions import Conflict
from common.decorators import log_activity, verify_id_token, is_authenticated
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import common.response_base as response_base
import common.firebase as firebase
import common as common
import logging

logger = logging.getLogger(__name__)
routes_router = APIRouter(prefix="/route", tags=["Routes"])

@routes_router.post("/add")
@log_activity
# @verify_id_token
@is_authenticated
def add_new_route(input: response_base.Add_New_Route = Body(...), token: str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    """
    Adds a new bus route to the database.
    """
    logger.info(f"Attempting to create new route: {input.route_name}")
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        name, uid = firebase.Name_and_UID(token)
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "RouteName": input.route_name,
            "RouteStops": input.stops,
            "RouteStart": input.start,
            "RouteEnd": input.end,
            "timing": [{
                "time": input.timing, 
                "delay_by": 0, 
                "deviation_sum": 0, 
                "deviation_count": 1, 
                "stop_name": input.start
                }],
            "lastUpdatedBy": f"{name} ({uid})"
        }
        doc_ref.create(document_data)  # Atomic create
        
        created_doc = doc_ref.get()
        response_data = created_doc.to_dict()
        
        # [LOGGING] Audit the creation of a new route
        firebase.log_to_firestore("ROUTE_CREATED", {"route": input.route_name}, uid, "INFO")
        
        logger.info(f"Route '{input.route_name}' created successfully.")
        return response_base.FireBaseResponse(
            message="Document created successfully with initial timing",
            data=response_data # type: ignore
        )
    except Conflict:
        logger.warning(f"Route '{input.route_name}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Route '{input.route_name}' already exists."
        )
    except Exception as e:
        # [LOGGING] Log failure to Firestore
        firebase.log_to_firestore("ERROR_CREATE_ROUTE", {"route": input.route_name, "error": str(e)}, "SYSTEM", "ERROR")
        
        logger.error(f"Failed to create route '{input.route_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create document",
                "error": str(e)
            }
        )
    
@routes_router.get("/routes", response_model=response_base.FireBaseResponse)
@log_activity
def get_routes() -> response_base.FireBaseResponse:
    """
    Get all bus routes.
    """
    try:
        logger.info("Fetching all bus routes")
        routes_ref = firebase.db.collection("busRoutes")
        routes = routes_ref.stream()
        all_routes = [route.id for route in routes]
        logger.info(f"All routes fetched successfully: {all_routes}")
        return response_base.FireBaseResponse(
            message="All routes fetched successfully",
            data=all_routes
        )
    except Exception as e:
        logger.error(f"Failed to fetch routes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch routes: {e}"
        )