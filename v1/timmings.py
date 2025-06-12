from datetime import datetime
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from fastapi import APIRouter, Body, HTTPException , status
from v1.common_decorators import log_activity, verify_id_token
import v1.common_response_base as response_base
import v1.base_firebase as firebase

routes_timming_router = APIRouter(prefix="/timings", tags=["Timings"])
# @routes_timming_router.get("/")
# def get_routes():
#     """Get all available routes."""
#     return {"message": "List of routes"}


def seconds_difference(t1: str, t2: str) -> int:
    # Parse times
    fmt = "%I:%M %p"
    today = datetime.today().date()
    dt1 = datetime.combine(today, datetime.strptime(t1, fmt).time())
    dt2 = datetime.combine(today, datetime.strptime(t2, fmt).time())
    # Calculate difference in seconds
    diff = (dt2 - dt1).total_seconds()
    return int(diff)

def firebase_add_new_route(input: response_base.Add_New_Route) -> response_base.FireBaseResponse:
    """
    Create a new document in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
             raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        decoded_token = firebase.auth.verify_id_token(input.token)
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "RouteName": input.route_name,
            "RouteStops": input.stops,
            "RouteStart": input.start,
            "RouteEnd": input.end,
            "timing": [input.timing],
            "lastUpdatedBy": f"{decoded_token.get('name')} ({decoded_token.get('uid')})"
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

def firebase_update_time(input: response_base.Firebase_Update_Time) -> response_base.FireBaseResponse:
    """
    Update a timing entry to the timing array of the specified route.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        decoded_token = firebase.auth.verify_id_token(input.token)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")
        
        time = doc.to_dict().get("timing", [])
        for t in time:
            if t.get("time") == input.list_time:
                avg = (t.get("deviation_sum") + seconds_difference(input.list_time, input.timing)) / (t.get("deviation_count") + 1)
                t["delay_by"] = avg
                t["deviation_sum"] += seconds_difference(input.list_time, input.timing)
                t["deviation_count"] += 1
                break

        document = {
            "timing": time,
            "lastUpdated": SERVER_TIMESTAMP,
            "lastUpdatedBy": f"{decoded_token.get('name')} ({decoded_token.get('uid')})"
            }
        doc_ref.update(document)
        return response_base.FireBaseResponse(
        message="Timing entry updated successfully",
                data={"timing": input.timing}
            )
             
    except Exception as e:
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Failed to update document",
                "error": error
            }
        )

def firebase_add_new_time(input: response_base.Firebase_Add_New_Time) -> response_base.FireBaseResponse:
    """
    Appends a new time in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if not doc.exists:
             raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")

        decoded_token = firebase.auth.verify_id_token(input.token)
        existing_timings = doc.to_dict().get("timing", [])
        updated_timings = existing_timings + [input.timing]
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "timing": updated_timings,
            "lastUpdatedBy": f"{decoded_token.get('name')} ({decoded_token.get('uid')})"
        }
        doc_ref.update(document_data)
        created_doc = doc_ref.get()
        response_data = created_doc.to_dict().get("timing", [])
        return response_base.FireBaseResponse(
            message="Document updated successfully with new timing",
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
