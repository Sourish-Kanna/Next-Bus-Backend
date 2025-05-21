import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from fastapi import APIRouter

# Get the Firebase credentials from the environment variable
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS_JSON is not set in environment variables")

# Parse the JSON string into a dictionary
cred_dict = json.loads(firebase_credentials_json)

# Initialize Firebase Admin SDK with the credentials
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Firestore Client
db = firestore.client()

firebase_router = APIRouter(prefix="/firebase", tags=["Firebase"])

@firebase_router.get("/test")
async def test_firebase() -> dict[str, dict|str]:
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