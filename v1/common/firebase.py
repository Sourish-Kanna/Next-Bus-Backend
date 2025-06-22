import logging
from os import getenv
from json import loads
from fastapi import HTTPException, status
from firebase_admin import credentials, initialize_app, firestore, auth

# Logging for Firebase initialization
logger = logging.getLogger(__name__)

firebase_app = None
db = None

def initialize_firebase():
    global firebase_app, db
    # Ensure that the environment variable FIREBASE_CREDENTIALS_JSON is set
    firebase_credentials_json = getenv('FIREBASE_CREDENTIALS_JSON')
    if not firebase_credentials_json:
        logger.error("FIREBASE_CREDENTIALS_JSON is not set in environment variables")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_CREDENTIALS_JSON is not set in environment variables"
        )
    cred_dict = loads(firebase_credentials_json)
    cred = credentials.Certificate(cred_dict)
    firebase_app = initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase initialized successfully")

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        logger.info("Token verified successfully")
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise Exception(e)

def get_token_details(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        logger.info("Token Data extracted successfully")
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
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
        is_admin = False
        if not user_id:
            logger.error("UID not found in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="UID not found in token"
            )

        logger.info(f"Fetching admin details for user ID: {user_id}")
        user_ref = db.collection("users").document(user_id) # type: ignore
        user_doc = user_ref.get()
        if not user_doc.exists:
            logger.error(f"User document not found for UID: {user_id}")
            is_admin = False
            
        user_data = user_doc.to_dict()
        is_admin = user_data.get("isAdmin", False) # type: ignore
        logger.info(f"User {user_id} isAdmin status: {is_admin}")

        user_details = {
            "sign_in_provider": decoded_token.get("firebase", {}).get("sign_in_provider", "Unknown"),
            "isAdmin": is_admin
        }
        logger.info(f"Admin user details fetched successfully: {user_details}")
        return user_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch admin user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )