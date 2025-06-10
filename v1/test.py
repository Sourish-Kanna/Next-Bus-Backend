from fastapi import APIRouter, Body
from v1.common_decorators import log_activity
from v1.common_response_base import FireBaseResponse , TokenRequest, RequestBody
import v1.base_firebase as firebase
from google.cloud.firestore_v1 import ArrayUnion, SERVER_TIMESTAMP

test_router = APIRouter(prefix="/test", tags=["Test"])

# @test_router.post("/test1", response_model=FireBaseResponse)
# # @verify_id_token
# @log_activity
# async def test_firebase(input: TokenRequest = Body(...)) -> FireBaseResponse:
#     """Test Firebase connection and list collections and documents."""
#     collections = [col.id for col in firebase.db.collections()]
#     collections_with_docs = {}
#     for col in firebase.db.collections():
#         doc_ids = [doc.id for doc in col.stream()]
#         collections_with_docs[col.id] = doc_ids

#     return FireBaseResponse(
#         message="Test successful",
#         data={
#             "collections": collections,
#             "collections_with_docs": collections_with_docs
#         }
#     )


@test_router.post("/verify_token", response_model=FireBaseResponse)
# @verify_id_token
@log_activity
def verify_firebase_token(input: TokenRequest = Body(...)) -> FireBaseResponse:
    """Verify Firebase ID token."""
    decoded_token = firebase.auth.verify_id_token(input.token)
    return FireBaseResponse(
        message="Token is valid",
        data={
            "token_details": decoded_token
        },
    )


@test_router.post("/test", response_model=FireBaseResponse)
def add_route_time(input: RequestBody = Body(...)) -> FireBaseResponse:
    """
    Append a new timing entry to the timing array of the specified route.
    If the route does not exist, create a new document in busRoutes/{route_name} with the specified fields.
    """
    doc_ref = firebase.db.collection("busRoutes").document(input.route_name)
    decoded_token = firebase.auth.verify_id_token(input.token)
    try:
        doc = doc_ref.get()
        if doc.exists:
            # Update: append to timing array and update lastUpdated fields
            doc_ref.update({
                "timing": ArrayUnion([input.timing]),
                "lastUpdated": SERVER_TIMESTAMP,
                "lastUpdatedBy": decoded_token.get("uid")
            })
            return FireBaseResponse(
                message="Timing entry added successfully",
                data={"timing": input.timing}
            )
        else:
            document_data = {
                "lastUpdated": SERVER_TIMESTAMP,
                "routeName": input.route_name,
                "stops": input.stops,
                "start": input.start,
                "end": input.end,
                "timing": [input.timing],
                "lastUpdatedBy": decoded_token.get("uid"),
            }
            doc_ref.set(document_data)
            return FireBaseResponse(
                message="Document created successfully with initial timing",
                data=document_data
            )
    except Exception as e:
        return FireBaseResponse(
            message="Failed to create or update document",
            error=str(e)
        )