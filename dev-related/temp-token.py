import firebase_admin
from firebase_admin import credentials, auth
import os
import json
import pyperclip
import requests
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Run it in the 'dev-related' folder.
# Make sure you have a 'dev.env' file in the root folder with the necessary environment variables.

# Load environment variables from dev.env in root file
load_dotenv(dotenv_path="../dev.env")

# IMPORTANT:
# 1. Set an environment variable named 'FIREBASE_CREDENTIALS_JSON'
#    containing the *entire content* of your service account JSON file as a string.
#    Example (in .env or terminal):
#    export FIREBASE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "...", ...}'
#
# 2. Set an environment variable named 'FIREBASE_WEB_API_KEY'.
#    You can find this in your Firebase Project Settings (General tab -> Web API Key).
#
# 3. This script now requires 'pyperclip' and 'requests'. Install them:
#    pip install pyperclip requests python-dotenv
#
# 4. Set an environment variable named 'FIREBASE_TEST_USER_ID'.
#    This is the User ID (UID) you want to mint a token for.
#    Example: export FIREBASE_TEST_USER_ID='my_test_user_uid_001'

# The User ID you want to create a token for.
# This can be any string.
# USER_ID_TO_MINT = "my_test_user_uid_001"
USER_ID_TO_MINT = os.getenv('FIREBASE_TEST_USER_ID')

# --- END CONFIGURATION ---

def get_id_token_from_custom_token(custom_token, web_api_key):
    """
    Exchanges a Firebase custom token for a full ID token by calling the
    Google Identity Toolkit REST API.
    """
    print("\nAttempting to exchange custom token for ID token...")
    
    identity_toolkit_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={web_api_key}"
    
    payload = {
        "token": custom_token,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(identity_toolkit_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        id_token = data.get('idToken')
        
        if not id_token:
            print("❌ ERROR: 'idToken' not found in API response.")
            # DO NOT log sensitive API response data
            if "error" in data and isinstance(data["error"], dict):
                print("API returned an error (details suppressed for security).")
            else:
                print("API returned an unexpected error format.")
            return None
            
        print("✅ Successfully exchanged for ID Token.")
        return id_token

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error during token exchange: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ An error occurred during token exchange: {e}")
        return None


def generate_real_custom_token():
    """
    Generates a real, valid Firebase Custom Token and exchanges it for an ID Token.
    The final ID Token is copied to the clipboard.
    """
    
    print("Attempting to generate a REAL Firebase Token...")
    print("---")

    # Get credentials from environment variable
    creds_json_string = os.getenv('FIREBASE_CREDENTIALS_JSON')
    web_api_key = os.getenv('FIREBASE_WEB_API_KEY')
    user_id = os.getenv('FIREBASE_TEST_USER_ID')
    
    if not creds_json_string:
        print(f"❌ ERROR: 'FIREBASE_CREDENTIALS_JSON' environment variable not set.")
        print(f"Please set this variable with the JSON content of your service account key.")
        return
        
    if not web_api_key:
        print(f"❌ ERROR: 'FIREBASE_WEB_API_KEY' environment variable not set.")
        print(f"Find it in your Firebase Project Settings (General tab).")
        return

    if not user_id:
        print(f"❌ ERROR: 'FIREBASE_TEST_USER_ID' environment variable not set.")
        print(f"Please set this to the UID you want to generate a token for.")
        return

    try:
        # Parse the JSON string from the environment variable
        creds_json = json.loads(creds_json_string)
        
        # Initialize the Firebase Admin SDK
        cred = credentials.Certificate(creds_json)
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
            
        print(f"✅ Firebase Admin SDK initialized.")

        # 1. Create the custom token
        custom_token_bytes = auth.create_custom_token(user_id)
        custom_token = custom_token_bytes.decode('utf-8')
        
        print(f"✅ Successfully created custom token for UID: '{user_id}'")

        # 2. Exchange custom token for an ID token
        id_token = get_id_token_from_custom_token(custom_token, web_api_key)
        
        if not id_token:
            print("---")
            print("❌ Failed to get final ID Token. See errors above.")
            return

        # 3. Copy the final ID token to clipboard
        bearer_token = "Bearer "
        try:
            bearer_token = f"Bearer {id_token}"
            pyperclip.copy(bearer_token)
            print("✅ Final 'Bearer' token copied to clipboard!")
        except Exception as e:
            print(f"⚠️ Warning: Could not copy to clipboard. ({e})")
            print("You may need to install 'xclip' or 'xsel' on Linux.")

        print(f"\nYour FINAL ID Token (copied to clipboard).")
        print("⚠️ For security, the full token is not printed to the console. Use your clipboard to paste it as needed.")
        print("\nTreat this token as a secret. Do not share or expose.")

    except json.JSONDecodeError:
        print(f"\n❌ An error occurred: Invalid JSON")
        print("Please ensure 'FIREBASE_CREDENTIALS_JSON' contains valid JSON.")
    except Exception as e:
        print(f"\n❌ An error occurred:")
        print(e)
        print("\nPlease ensure your 'FIREBASE_CREDENTIALS_JSON' variable is set correctly.")

if __name__ == "__main__":
    generate_real_custom_token()