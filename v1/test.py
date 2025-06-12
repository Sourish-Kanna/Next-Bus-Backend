from fastapi import APIRouter, Body, HTTPException, status
import v1.common_response_base as response_base
import v1.base_firebase as firebase
import v1.timmings as timmings

test_router = APIRouter(prefix="/test", tags=["Test"])

@test_router.post("/add")
def add_new_route(input: response_base.Add_New_Route = Body(...)) -> response_base.FireBaseResponse:
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if doc.exists:
            raise Exception(f"{status.HTTP_409_CONFLICT} Document Exists, Update it")

        return timmings.firebase_add_new_route(input)
    
    except Exception as e:
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Error adding timing entry",
                "error": error
            }
        )

@test_router.post("/update")
def update_time(input: response_base.Update_Time = Body(...)) -> response_base.FireBaseResponse:
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    try:
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception(f"{status.HTTP_404_NOT_FOUND} Document Does not exist, Create it first")

        doc = doc.to_dict()
        timing = doc.get("timing", [])
        input_time: str = input.timing
        for time in timing:
            if 0 <= timmings.seconds_difference(time.get("time"), input_time) <= 300: # 300 sec is 5 Minutes
                new = response_base.Firebase_Update_Time(
                    token=input.token, 
                    route_name=input.route_name, 
                    timing=input.timing, 
                    list_time= time.get("time")
                    )
                return timmings.firebase_update_time(new)
            
        time = timing[0]
        time["time"] = input_time
        time["delay_by"] = 0
        time["deviation_sum"] = 0
        time["deviation_count"] = 1
        time["stop_name"] = input.stop
        new_input = response_base.Firebase_Add_New_Time(
            token=input.token, 
            route_name=doc.get("RouteName"),
            timing= time,
            )
        return timmings.firebase_add_new_time(new_input)
        
    except Exception as e:
        status_code, error = str(e).split(maxsplit=1)
        raise HTTPException(
            status_code=int(status_code),
            detail={
                "message": "Error updating timing entry",
                "error": error
            }
        )
