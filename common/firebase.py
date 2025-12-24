import logging
from os import getenv
from json import loads
from fastapi import HTTPException, status
import firebase_admin
from firebase_admin import credentials, initialize_app, firestore, auth
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

# Logging for Firebase initialization
logger = logging.getLogger(__name__)

firebase_app = None
db = None
def initialize_firebase():
    global firebase_app, db

    cred = None
    cred_dict = None
    
    firebase_credentials_json = getenv("FIREBASE_CREDENTIALS_JSON")
    if not firebase_credentials_json:
        logger.error("No Firebase credentials found: set FIREBASE_CREDENTIALS_JSON")
        raise ValueError("Firebase credentials not provided")
    try:
        cred_dict = loads(firebase_credentials_json)
    except Exception:
        try:
            fixed_json = firebase_credentials_json.replace("\\n", "\n")
            cred_dict = loads(fixed_json)
        except Exception as e:
            logger.error(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
            raise
    cred = credentials.Certificate(cred_dict)

    if not firebase_admin._apps:
        firebase_app = initialize_app(cred)
        db = firestore.client()
        logger.info("Firebase initialized successfully")
    else:
        logger.warning("Firebase app already initialized; skipping initialization")
        if not db:
            db = firestore.client()

def verify_token(id_token):
    try:
        auth.verify_id_token(id_token)
        logger.info("Token verified successfully")
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise Exception(e)

def get_token_details(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        logger.info("Token Data extracted successfully")
        return decoded_token
    except Exception as e:
        logger.error(f"Token Data extraction failed: {e}")
        raise Exception(e)

def create_custom_token(uid):
    try:
        custom_token = auth.create_custom_token(uid)
        logger.info(f"Custom token created for UID: {uid}")
        return custom_token.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to create custom token for UID {uid}: {e}")
        raise Exception(e)

def Name_and_UID(token):
    decoded_token = get_token_details(token)
    logger.info(f"Extracted name and UID from token: {decoded_token.get('name')}, {decoded_token.get('uid')}")
    return decoded_token.get("name"), decoded_token.get("uid")

def get_admin_details(token):
    try:
        decoded_token = get_token_details(token)
        user_id = decoded_token.get("uid")
        sign_in_provider = decoded_token.get("firebase", {}).get("sign_in_provider", None)
        is_admin = False
        is_logged_in = False # Non admin user but logged in
        is_guest = False
        allowed_providers = ["password", "google.com"]
        if getenv("DEV_ENV", "false").lower() == "true":
            allowed_providers.append("custom")

        if user_id and sign_in_provider in allowed_providers:
            is_logged_in = True
            user_ref = db.collection("users").document(user_id)  # type: ignore
            user_doc = user_ref.get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                is_admin = user_data.get("isAdmin", False)  # type: ignore
            else:
                is_admin = False
        elif sign_in_provider == "anonymous":
            is_logged_in = False
            is_admin = False
            is_guest = True
        else:
            is_logged_in = False
            is_admin = False
            is_guest = False
            logger.warning(f"Unrecognized sign-in provider: {sign_in_provider}")

        user_details = {
            "isAdmin": is_admin,
            "isLoggedIn": is_logged_in,
            "isGuest": is_guest,
            "sign_in_provider": sign_in_provider if sign_in_provider else "unknown",
        }
        logger.info(f"User details fetched: {user_details}")
        return user_details
    except Exception as e:
        logger.error(f"Failed to fetch admin user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )

# def log_to_firestore(action: str, details: dict, user_id: str, level: str = "INFO"):
#     """
#     Saves a system log to the 'systemLogs' collection in Firestore.
#     Used ONLY for Warnings, Errors, or Critical Actions to save costs.
#     """
#     try:
#         if db is not None:
#             db.collection("systemLogs").add({
#                 "timestamp": SERVER_TIMESTAMP,
#                 "action": action,
#                 "level": level,
#                 "userId": user_id,
#                 "details": details
#             })
#         else:
#             logger.warning("Firestore DB not initialized, skipping log_to_firestore")
#     except Exception as e:
#         # Never fail the main request just because logging failed
#         logger.error(f"Failed to write system log: {e}")
