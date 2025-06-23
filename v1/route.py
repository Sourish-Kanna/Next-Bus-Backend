from fastapi import APIRouter, Body, HTTPException , status, Depends
from v1.common.decorators import log_activity, verify_id_token
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import v1.common.response_base as response_base
import v1.common.firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
routes_router = APIRouter(prefix="/route", tags=["Routes"])

def firebase_add_new_route(input: response_base.Add_New_Route, token: str) -> response_base.FireBaseResponse:
    """
    Create a new document in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
             logger.warning(f"Route '{input.route_name}' already exists.")
             raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        name, uid = firebase.Name_and_UID(token)
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "RouteName": input.route_name,
            "RouteStops": input.stops,
            "RouteStart": input.start,
            "RouteEnd": input.end,
            "timing": [input.timing],
            "lastUpdatedBy": f"{name} ({uid})"
        }
        doc_ref.set(document_data)
        created_doc = doc_ref.get()
        response_data = created_doc.to_dict()
        logger.info(f"Route '{input.route_name}' created successfully.")
        return response_base.FireBaseResponse(
            message="Document created successfully with initial timing",
            data=response_data # type: ignore
        )
    except Exception as e:
        logger.error(f"Failed to create route '{input.route_name}': {e}")
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Failed to create document",
                "error": error
            }
        )

@routes_router.post("/add")
@verify_id_token
@log_activity
def add_new_route(input: response_base.Add_New_Route = Body(...), token: str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
            logger.warning(f"Route '{input.route_name}' already exists.")
            raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        logger.info(f"Adding new route: {input.route_name}")
        return firebase_add_new_route(input,token)
    
    except Exception as e:
        logger.error(f"Error adding timing entry for route '{input.route_name}': {e}")
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Error adding timing entry",
                "error": error
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