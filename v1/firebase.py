from fastapi import APIRouter
import v1

firebase_router = APIRouter(prefix="/firebase", tags=["Firebase"])
db = v1.db  # Use the Firestore client from v1 module

@firebase_router.get("/test")
@v1.log_activity
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