from .auth import auth_router
from .test import test_router
from .firebase import firebase_router
from .cust_logging import log_activity
from fastapi import HTTPException

from firebase_admin import credentials, initialize_app, firestore, auth
import os
import json

__all__ = ["auth_router", "test_router", "firebase_router", "log_activity"]


# Initialize Firestore once at the package level

# Get the Firebase credentials from the environment variable
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