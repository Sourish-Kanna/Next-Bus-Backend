import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

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
