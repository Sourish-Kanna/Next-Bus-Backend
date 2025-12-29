from fastapi import APIRouter, Body, HTTPException , status, Depends
from common.decorators import log_activity, is_authenticated
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import common.response_base as response_base
import common.firebase as firebase
import common as common
import logging
from v1.future import save_historical_data, isRateLimitExceeded

logger = logging.getLogger(__name__)
timing_router = APIRouter(prefix="/timings", tags=["Timings"])

def firebase_update_time(input: response_base.Firebase_Update_Time, token: str ) -> response_base.FireBaseResponse:
    """
    Update an existing timing entry to the timing array of the specified route.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        name, uid = firebase.Name_and_UID(token)
        doc = doc_ref.get()

        time = doc.to_dict().get("timing", []) # type: ignore
        current_delay = 0
        
        for t in time:
            if t.get("time") == input.list_time:
                # Calculate the specific delay for this report
                this_entry_delay = common.seconds_difference(input.list_time, input.timing)
                
                # Update the running average (for the App UI)
                t["deviation_sum"] += this_entry_delay
                t["deviation_count"] += 1
                avg = t.get("deviation_sum") / t.get("deviation_count")
                t["delay_by"] = avg
                
                current_delay = this_entry_delay
                break

        # Update the Main Route Document (For App UI)
        document = {
            "timing": time,
            "lastUpdated": SERVER_TIMESTAMP,
            "lastUpdatedBy": f"{name} ({uid})"
        }
        doc_ref.update(document)

        logger.info(f"Timing entry updated for route '{input.route_name}' by {uid}.")

        # Save Historical Data (Essential for future AI)
        save_historical_data(
            route_name=input.route_name,
            reported_time=input.timing,
            official_time=input.list_time,
            delay=current_delay,
            user_id=uid
        )

        return response_base.FireBaseResponse(
            message="Timing entry updated successfully",
            data={"timing": input.timing}
        )
             
    except HTTPException as he:
        raise he 
    
    except Exception as e:
        # firebase.log_to_firestore("ERROR_UPDATE_TIMING", {"route": input.route_name, "error": str(e)}, "SYSTEM", "ERROR")
        
        logger.error(f"Failed to update timing for route '{input.route_name}': {e}")
        status_code = getattr(e, "status_code", 500)
        error = str(e)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Failed to update document",
                "error": error
            }
        )

def firebase_add_new_time(input: response_base.Firebase_Add_New_Time, token: str) -> response_base.FireBaseResponse:
    """
    Appends a new time entry to the timing array of the specified route.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        name, uid = firebase.Name_and_UID(token)
        existing_timings = doc.to_dict().get("timing", []) # type: ignore
        updated_timings = existing_timings + [input.timing]
        document_data = {
            "lastUpdated": SERVER_TIMESTAMP,
            "timing": updated_timings,
            "lastUpdatedBy": f"{name} ({uid})"
        }
        doc_ref.update(document_data)
        timming = input.timing
        save_historical_data(
            route_name=input.route_name,
            reported_time=timming.get("time"), # type: ignore
            official_time=timming.get("time"), # type: ignore
            delay=timming.get("delay_by"), # type: ignore
            user_id=uid
        )
        created_doc = doc_ref.get()
        response_data = created_doc.to_dict().get("timing", []) # type: ignore
        logger.info(f"New timing added for route '{input.route_name}'.")
        return response_base.FireBaseResponse(
            message="Document updated successfully with new timing",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Failed to add new timing for route '{input.route_name}': {e}")
        raise Exception(e)

@timing_router.put("/update")
@log_activity
@is_authenticated
def update_time(input: response_base.Update_Time = Body(...), token:str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    try:
        doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning(f"Route '{input.route_name}' does not exist for update_time endpoint.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document Does not exist, Create it first"
            )
        
        if isRateLimitExceeded(token, input.route_name, "busRoutes"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You are updating too fast. Please wait a minute for route {input.route_name}"
            )
        
        doc_dict = doc.to_dict()
        timing = doc_dict.get("timing", []) # type: ignore
        input_time = input.timing
        
        # Check existing times and update if within threshold
        for time in timing:
            try:
                diff = abs(common.seconds_difference(input_time, time.get("time")))
                if diff <= 300:  # Within 5 minutes
                    new = response_base.Firebase_Update_Time(
                        route_name=input.route_name, 
                        timing=input_time, 
                        list_time=time.get("time")
                    )
                    logger.info(f"Updating existing timing for route '{input.route_name}'.")
                    return firebase_update_time(new, token)
            except Exception as e:
                logger.warning(f"Time comparison failed: {e}, continuing to next time")
                continue

        # If no matching time found, add new time
        new_time = {
            "time": input_time,
            "delay_by": 0,
            "deviation_sum": 0,
            "deviation_count": 1,
            "stop_name": input.stop
        }
        
        new_input = response_base.Firebase_Add_New_Time(
            route_name=input.route_name,
            timing=new_time,
        )
        logger.info(f"Adding new timing for route '{input.route_name}'.")
        return firebase_add_new_time(new_input, token)
        
    except HTTPException as he:
        raise he
    
    except Exception as e:
        logger.error(f"Error updating timing entry for route '{input.route_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "message": "Error updating timing entry",
                "error": str(e)
            }
        )

@timing_router.get("/{route_name}")
@log_activity
def get_time(route_name: str) -> response_base.FireBaseResponse:
    """
    Get timing details for a specific route.
    """
    try:
        logger.info(f"Fetching timing details for route: {route_name}")
        doc_ref = firebase.db.collection("busRoutes").document(route_name)
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Route '{route_name}' does not exist.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found, Add it first"
            )
        timing_data = [
            {
                "time":t.get("time"), 
                "stop": t.get("stop_name"), 
                "delay": t.get("delay_by")
            } for t in doc.to_dict().get("timing", [])]  # type: ignore
        sorted_timing = sorted(timing_data, key=lambda x: common.convert_to_24hr(x["time"]))
        logger.info(f"Timing details fetched successfully for route '{route_name}': {len(timing_data)}")
        return response_base.FireBaseResponse(
            message="Timing details fetched successfully",
            data=sorted_timing
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to fetch timing details for route '{route_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch timing details: {e}"
        )