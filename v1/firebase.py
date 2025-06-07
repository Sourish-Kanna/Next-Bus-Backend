import os
import json
from fastapi import APIRouter, HTTPException, Body
from firebase_admin import credentials, initialize_app, firestore, auth
from v1.cust_logging import log_activity
from v1.return_type import FireBaseResponse, TokenRequest

# Initialize Firestore and Get the Firebase credentials from the environment variable
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS_JSON is not set in environment variables")
cred_dict = json.loads(firebase_credentials_json)
cred = credentials.Certificate(cred_dict)
firebase_app = initialize_app(cred)
db = firestore.client()

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token or user not found")


firebase_router = APIRouter(prefix="/firebase", tags=["Firebase"])

@firebase_router.post("/test", response_model=FireBaseResponse)
@log_activity
async def test_firebase(id_token: str) -> FireBaseResponse:
    """Test Firebase connection and list collections and documents."""
    verify_token(id_token)
    collections = [col.id for col in db.collections()]
    collections_with_docs = {}
    for col in db.collections():
        doc_ids = [doc.id for doc in col.stream()]
        collections_with_docs[col.id] = doc_ids

    return FireBaseResponse(
        message="Test successful",
        data={
            "collections": collections,
            "collections_with_docs": collections_with_docs
        }
    )


@firebase_router.post("/verify_token", response_model=FireBaseResponse)
@log_activity
def verify_firebase_token(id_token: str) -> FireBaseResponse:
    """Verify Firebase ID token."""
    decoded_token = verify_token(id_token)
    return FireBaseResponse(
        message="Token is valid",
        data=decoded_token,
        status_code=200
    )