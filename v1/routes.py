
from fastapi import APIRouter, Body
from v1.decorators import log_activity, verify_id_token
from v1.response_base import FireBaseResponse, TokenRequest
import v1.firebase as firebase

routes_router = APIRouter(prefix="/routes", tags=["Firebase"])


@routes_router.post("/test", response_model=FireBaseResponse)
@log_activity
@verify_id_token
async def test_firebase() -> FireBaseResponse:
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


@routes_router.post("/verify_token", response_model=FireBaseResponse)
@log_activity
def verify_firebase_token(token_request: TokenRequest = Body(...)) -> FireBaseResponse:
    """Verify Firebase ID token."""
    decoded_token = firebase.verify_token(token_request.id_token)
    return FireBaseResponse(
        message="Token is valid",
        data=decoded_token,
        status_code=200
    )