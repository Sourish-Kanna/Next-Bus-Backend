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

def create_custom_token(uid):
    try:
        custom_token = auth.create_custom_token(uid)
        logger.info(f"Custom token created for UID: {uid}")
        return custom_token.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to create custom token for UID {uid}: {e}")
        raise Exception(e)

def Name_and_UID(token):
    decoded_token = verify_token(token)
    logger.info(f"Extracted name and UID from token: {decoded_token.get('name')}, {decoded_token.get('uid')}")
    return decoded_token.get("name"), decoded_token.get("uid")

