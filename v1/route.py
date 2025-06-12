from os import name
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from fastapi import APIRouter, Body, HTTPException , status
from v1.common_decorators import log_activity, verify_id_token
import v1.common_response_base as response_base
import v1.base_firebase as firebase

routes_router = APIRouter(prefix="/route", tags=["Routes"])

def firebase_add_new_route(input: response_base.Add_New_Route) -> response_base.FireBaseResponse:
    """
    Create a new document in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
             raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        name, uid = firebase.Name_and_UID(input.token)
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
        return response_base.FireBaseResponse(
            message="Document created successfully with initial timing",
            data=response_data
        )
    except Exception as e:
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
def add_new_route(input: response_base.Add_New_Route = Body(...)) -> response_base.FireBaseResponse:
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
            raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        return firebase_add_new_route(input)
    
    except Exception as e:
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Error adding timing entry",
                "error": error
            }
        )