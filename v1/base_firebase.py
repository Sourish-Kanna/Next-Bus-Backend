from os import getenv
from json import loads
from fastapi import HTTPException, status
from firebase_admin import credentials, initialize_app, firestore, auth

# Ensure that the environment variable FIREBASE_CREDENTIALS_JSON is set
firebase_credentials_json = getenv('FIREBASE_CREDENTIALS_JSON')
if not firebase_credentials_json:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="FIREBASE_CREDENTIALS_JSON is not set in environment variables")
cred_dict = loads(firebase_credentials_json)
cred = credentials.Certificate(cred_dict)

# Initialize Firebase app and Firestore client
firebase_app = initialize_app(cred)
db = firestore.client()

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise Exception(e)


def create_custom_token(uid):
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token.decode('utf-8')
    except Exception as e:
        raise Exception(e)

def Name_and_UID(token):
    decoded_token = verify_token(token)
    return decoded_token.get("name"), decoded_token.get("uid")

