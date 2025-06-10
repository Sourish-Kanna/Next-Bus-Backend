from pydantic import BaseModel


class ResponseModel(BaseModel):
    status_code: int = 200
    success: bool = True
    message: str

class FireBaseResponse(ResponseModel):
    data: dict | None = None

class Add_Time(BaseModel):
    token: str
    route_name: str
    stops: list[str]
    start: str
    end: str
    timing: dict | str

class TokenRequest(BaseModel):
    token: str | None

