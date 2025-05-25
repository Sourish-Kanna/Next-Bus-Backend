import os
import json
from fastapi import APIRouter, HTTPException
from firebase_admin import credentials, initialize_app, firestore, auth

from .cust_logging import log_activity

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
        raise HTTPException(status_code=401, detail="Invalid token")


firebase_router = APIRouter(prefix="/firebase", tags=["Firebase"])

@firebase_router.get("/test")
@log_activity
async def test_firebase() -> dict[str, dict | str]:
    """Test Firebase connection and list collections and documents."""
    collections = [col.id for col in db.collections()]
    collections_with_docs = {}
    for col in db.collections():
        doc_ids = [doc.id for doc in col.stream()]
        collections_with_docs[col.id] = doc_ids

    return {
        "message": "Test successful",
        "data": {
            "collections": collections,
            "collections_with_docs": collections_with_docs
        }
    }