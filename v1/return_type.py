from pydantic import BaseModel


class Item(BaseModel):
    text: str
    is_done: bool = False
    status_code: int = 200

class ResponseModel(BaseModel):
    status_code: int = 200
    success: bool = True
    error: str | None = None
    message: str

class FireBaseResponse(ResponseModel):
    data: dict

class TokenRequest(BaseModel):
    id_token: str

class FirestoreDocument(BaseModel):
    id: str
    data: dict