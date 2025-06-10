from pydantic import BaseModel


class ResponseModel(BaseModel):
    status_code: int = 200
    success: bool = True
    error: str | None = None
    message: str

class FireBaseResponse(ResponseModel):
    data: dict | None = None

class Add_Time(BaseModel):
    token: str
    route_name: str
    stops: list[str]
    start: str
    end: str
    timing: list[dict]
    last_updated: str
    last_updated_by: str

class TokenRequest(BaseModel):
    token: str | None