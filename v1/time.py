from fastapi import APIRouter, Body, HTTPException , status, Depends
from v1.common.decorators import log_activity, verify_id_token
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import v1.common.response_base as response_base
import v1.common.firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
timming_router = APIRouter(prefix="/timings", tags=["Timings"])

def firebase_update_time(input: response_base.Firebase_Update_Time, token: str ) -> response_base.FireBaseResponse:
    """
    Update a timing entry to the timing array of the specified route.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        name, uid = firebase.Name_and_UID(token)
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Route '{input.route_name}' does not exist for timing update.")
            raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")
        
        time = doc.to_dict().get("timing", [])
        for t in time:
            if t.get("time") == input.list_time:
                avg = (t.get("deviation_sum") + common.seconds_difference(input.list_time, input.timing)) / (t.get("deviation_count") + 1)
                t["delay_by"] = avg
                t["deviation_sum"] += common.seconds_difference(input.list_time, input.timing)
                t["deviation_count"] += 1
                break

        document = {
            "timing": time,
            "lastUpdated": SERVER_TIMESTAMP,
            "lastUpdatedBy": f"{name} ({uid})"
            }
        doc_ref.update(document)
        logger.info(f"Timing entry updated for route '{input.route_name}'.")
        return response_base.FireBaseResponse(
        message="Timing entry updated successfully",
                data={"timing": input.timing}
            )
             
    except Exception as e:
        logger.error(f"Failed to update timing for route '{input.route_name}': {e}")
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Failed to update document",
                "error": error
            }
        )

def firebase_add_new_time(input: response_base.Firebase_Add_New_Time, token: str) -> response_base.FireBaseResponse:
    """
    Appends a new time in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Route '{input.route_name}' does not exist for adding new time.")
            raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")

        name, uid = firebase.Name_and_UID(token)
        existing_timings = doc.to_dict().get("timing", [])
        updated_timings = existing_timings + [input.timing]
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "timing": updated_timings,
            "lastUpdatedBy": f"{name} ({uid})"
        }
        doc_ref.update(document_data)
        created_doc = doc_ref.get()
        response_data = created_doc.to_dict().get("timing", [])
        logger.info(f"New timing added for route '{input.route_name}'.")
        return response_base.FireBaseResponse(
            message="Document updated successfully with new timing",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Failed to add new timing for route '{input.route_name}': {e}")
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Failed to create document",
                "error": error
            }
        )

@timming_router.post("/update")
@verify_id_token
@log_activity
def update_time(input: response_base.Update_Time = Body(...), token:str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Route '{input.route_name}' does not exist for update_time endpoint.")
            raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")

        doc = doc.to_dict()
        timing = doc.get("timing", [])
        input_time: str = input.timing
        for time in timing:
            if 0 <= common.seconds_difference(time.get("time"), input_time) <= 300: # 300 sec is 5 Minutes
                new = response_base.Firebase_Update_Time(
                    route_name=input.route_name, 
                    timing=input.timing, 
                    list_time= time.get("time")
                    )
                logger.info(f"Updating existing timing for route '{input.route_name}'.")
                return firebase_update_time(new, token)
            
        time = timing[0]
        time["time"] = input_time
        time["delay_by"] = 0
        time["deviation_sum"] = 0
        time["deviation_count"] = 1
        time["stop_name"] = input.stop
        new_input = response_base.Firebase_Add_New_Time(
            route_name=doc.get("RouteName"),
            timing= time,
            )
        logger.info(f"Adding new timing for route '{input.route_name}'.")
        return firebase_add_new_time(new_input, token)
        
    except Exception as e:
        logger.error(f"Error updating timing entry for route '{input.route_name}': {e}")
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Error updating timing entry",
                "error": error
            }
        )
    