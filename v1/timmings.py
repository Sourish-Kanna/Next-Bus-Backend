from google.cloud.firestore_v1 import ArrayUnion
from fastapi import APIRouter, Body
from v1.common_decorators import log_activity, verify_id_token
from v1.common_response_base import FireBaseResponse, RequestBody
import v1.base_firebase as firebase

routes_timming_router = APIRouter(prefix="/timings", tags=["Timings"])

@routes_timming_router.get("/")
def get_routes():
    """Get all available routes."""
    return {"message": "List of routes"}

@routes_timming_router.post("/add")
@log_activity
@verify_id_token
def add_route_time(input: RequestBody = Body(...)) -> FireBaseResponse:
    """
    Append a new timing entry to the timing array of the specified route.
    If the route does not exist, create a new document in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
            # Update: append to timing array and update lastUpdated fields
            doc_ref.update({
                "timing": ArrayUnion([input.timing]),
                "lastUpdated": input.last_updated,
                "lastUpdatedBy": input.last_updated_by
            })
            return FireBaseResponse(
                message="Timing entry added successfully",
                data={"timing": input.timing}
            )
        else:
            # Create: new document with all fields
            document_data = {
                "lastUpdated": input.last_updated,
                "routeName": input.route_name,
                "stops": input.stops,
                "start": input.start,
                "end": input.end,
                "timing": [input.timing],
                "lastUpdatedBy": input.last_updated_by
            }
            doc_ref.set(document_data)
            return FireBaseResponse(
                message="Document created successfully with initial timing",
                data=document_data
            )
    except Exception as e:
        return FireBaseResponse(
            message="Failed to create or update document",
            error=str(e)
        )