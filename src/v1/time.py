from fastapi import APIRouter, Body, HTTPException, Request , status, Depends, Query
from common.decorators import log_activity, is_authenticated
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import common.response as response
import common.firebase as firebase
import common as common
import logging
from v1.future import save_historical_data, isRateLimitExceeded
from main import limiter

logger = logging.getLogger(__name__)
timing_router = APIRouter(prefix="/timings", tags=["Timings"])

def firebase_update_time(input: response.Firebase_Update_Time, token: str ) -> response.FireBaseResponse:
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

        return response.FireBaseResponse(
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

def firebase_add_new_time(input: response.Firebase_Add_New_Time, token: str) -> response.FireBaseResponse:
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
        return response.FireBaseResponse(
            message="Document updated successfully with new timing",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Failed to add new timing for route '{input.route_name}': {e}")
        raise Exception(e)

@timing_router.put("/update")
@limiter.limit("5/minute")
@log_activity
@is_authenticated
def update_time(request: Request, input: response.Update_Time = Body(...), token:str = Depends(common.get_token_from_header)) -> response.FireBaseResponse:
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
                    new = response.Firebase_Update_Time(
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
        
        new_input = response.Firebase_Add_New_Time(
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

""" @timing_router.delete("/{route}")
@log_activity
@is_authenticated
def delete_timing_entry(
    route: str,
    time: str = Query(..., description="Entry time in format like 01:30 PM"),
    token: str = Depends(common.get_token_from_header)
) -> response_base.FireBaseResponse:
    " ""
    # Reverse one aggregated timing contribution for a route/time slot.
    " ""
    try:
        # Validate input time format early to provide a clear 400 error.
        try:
            common.convert_to_24hr(time)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use format like 01:30 PM"
            )

        doc_ref = firebase.db.collection("busRoutes").document(route)
        doc = doc_ref.get()

        if not doc.exists:
            logger.warning(f"Route '{route}' does not exist for delete_timing_entry endpoint.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found, Add it first"
            )

        route_data = doc.to_dict() or {}
        timings = route_data.get("timing", [])

        target_index = -1
        matched_time = None
        for i, entry in enumerate(timings):
            try:
                diff = abs(common.seconds_difference(time, entry.get("time")))
                if diff <= 300:  # Within 5 minutes, same as update_time matching rule
                    target_index = i
                    matched_time = entry.get("time")
                    break
            except Exception as e:
                logger.warning(f"Time comparison failed in delete_timing_entry: {e}, continuing")
                continue

        if target_index == -1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Timing entry '{time}' not found for route '{route}'"
            )

        target = timings[target_index]
        current_sum = float(target.get("deviation_sum", 0) or 0)
        current_count = int(target.get("deviation_count", 0) or 0)
        this_entry_delay = float(target.get("delay_by", 0) or 0)

        if current_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Timing entry '{time}' has zero reports; nothing to reverse"
            )

        new_sum = current_sum - this_entry_delay
        new_count = current_count - 1

        if new_count <= 0:
            timings.pop(target_index)
            target = {}
        else:
            if new_sum < 0:
                new_sum = 0
            target["deviation_sum"] = new_sum
            target["deviation_count"] = new_count
            target["delay_by"] = new_sum / new_count

        name, uid = firebase.Name_and_UID(token)
        doc_ref.update({
            "timing": timings,
            "lastUpdated": SERVER_TIMESTAMP,
            "lastUpdatedBy": f"{name} ({uid})"
        })

        logger.info(f"Timing entry '{time}' reversed for route '{route}' by {uid}.")
        message = "Timing entry deleted successfully" if new_count <= 0 else "Timing entry reversed successfully"
        return response_base.FireBaseResponse(
            message=message,
            data={
                "route": route,
                "requested_time": time,
                "matched_time": matched_time,
                "deleted": new_count <= 0,
                "deviation_sum": target.get("deviation_sum", 0),
                "deviation_count": target.get("deviation_count"),
                "delay_by": target.get("delay_by")
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to reverse timing entry '{time}' for route '{route}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to reverse timing entry",
                "error": str(e)
            }
        ) """

@timing_router.get("/{route_name}")
@limiter.limit("100/minute")
@log_activity
def get_time(request: Request, route_name: str) -> response.FireBaseResponse:
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
                "delay": t.get("delay_by"),
                "count": t.get("deviation_count"),
            } for t in doc.to_dict().get("timing", [])]  # type: ignore
        sorted_timing = sorted(timing_data, key=lambda x: common.convert_to_24hr(x["time"]))
        logger.info(f"Timing details fetched successfully for route '{route_name}': {len(timing_data)}")
        return response.FireBaseResponse(
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