from pydantic import BaseModel

class ResponseModel(BaseModel):
    status_code: int = 200
    message: str

class FireBaseResponse(ResponseModel):
    data: dict | list

class Add_New_Route(BaseModel):
    route_name: str
    stops: list[str]
    start: str
    end: str
    timing: str

class Firebase_Add_New_Time(BaseModel):
    route_name: str
    timing: dict

class Update_Time(BaseModel):
    route_name: str
    timing: str
    stop: str

class Firebase_Update_Time(BaseModel):
    route_name: str
    timing: str
    list_time: str

class TokenRequest(BaseModel):
    token: str

