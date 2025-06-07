from fastapi import APIRouter, Body
from v1.decorators import log_activity, verify_id_token
from v1.response_base import FireBaseResponse, TokenRequest
import v1.firebase as firebase

test_router = APIRouter(prefix="/test", tags=["Firebase"])

@test_router.post("/test", response_model=FireBaseResponse)
@verify_id_token
@log_activity
async def test_firebase(token_request: TokenRequest = Body(...)) -> FireBaseResponse:
    """Test Firebase connection and list collections and documents."""
    collections = [col.id for col in firebase.db.collections()]
    collections_with_docs = {}
    for col in firebase.db.collections():
        doc_ids = [doc.id for doc in col.stream()]
        collections_with_docs[col.id] = doc_ids

    return FireBaseResponse(
        message="Test successful",
        data={
            "collections": collections,
            "collections_with_docs": collections_with_docs
        }
    )


@test_router.post("/verify_token", response_model=FireBaseResponse)
@verify_id_token
@log_activity
def verify_firebase_token(token_request: TokenRequest = Body(...)) -> FireBaseResponse:
    """Verify Firebase ID token."""
    return FireBaseResponse(
        message="Token is valid",
        data={"id_token": token_request.id_token},
        status_code=200
    )