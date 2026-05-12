from fastapi import APIRouter, HTTPException, Request, status, Depends
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import common.response as response
from common.decorators import log_activity
import common.firebase as firebase
import common as common
import logging
from main import limiter

logger = logging.getLogger(__name__)
user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.get("/get-user-details")
@limiter.limit("10/minute")
@log_activity
def get_user_details(request: Request, token:str = Depends(firebase.get_user_token)) -> response.FireBaseResponse:
    """Get User Details"""
    user_uid = "unknown"
    try:
        decoded = firebase.get_token_details(token)
        user_uid = decoded.get("uid", "unknown")
    except:
        pass

    try:
        logger.info("Fetching user details")
        detail = firebase.get_admin_details(token)
        if not detail:
            logger.warning("User details not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User details not found"
            )
        
        # if detail.get("isAdmin") is True:
        #     firebase.log_to_firestore(
        #         action="ADMIN_ACCESS",
        #         details={"provider": detail.get("sign_in_provider")},
        #         user_id=user_uid,
        #         level="WARNING"
        #     )
        
        logger.info(f"User details fetched successfully for {user_uid} (Admin: {detail.get('isAdmin')})")
        
        return response.FireBaseResponse(
            message="User details fetched successfully",
            data=detail,
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        # firebase.log_to_firestore(
        #     action="ERROR_FETCH_USER",
        #     details={"error": str(e)},
        #     user_id=user_uid,
        #     level="ERROR"
        # )
        
        logger.error(f"Failed to fetch user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )

@user_router.post("/sync")
@limiter.limit("5/minute")
@log_activity
def sync_user(request: Request, token:str = Depends(firebase.get_user_token)) -> response.FireBaseResponse:
    """
    Called from the frontend right after Firebase Auth sign-in.
    Creates a user document in Firestore ONLY for permanent accounts (e.g., Google, Email).
    Ignores Anonymous users to prevent database bloat.
    """
    try:
        decoded_token = firebase.get_token_details(token)
        uid = decoded_token.get("uid")
        
        # 1. Check the Sign-In Provider
        firebase_info = decoded_token.get("firebase", {})
        sign_in_provider = firebase_info.get("sign_in_provider", "unknown")
        
        # 2. Block Anonymous Users
        if sign_in_provider == "anonymous":
            logger.info(f"Skipped database sync for anonymous user: {uid}")
            return response.FireBaseResponse(
                message="Anonymous users are not saved to the database.",
                data={"isNewUser": False, "isAnonymous": True}
            )

        # 3. Process Google / Email Users
        email = decoded_token.get("email", "")
        name = decoded_token.get("name", "")

        user_ref = firebase.db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            # Create the initial user profile
            user_ref.set({
                "uid": uid,
                "email": email,
                "name": name,
                "isAdmin": False,
                "createdAt": SERVER_TIMESTAMP,
                "lastLogin": SERVER_TIMESTAMP
            })
            logger.info(f"New permanent user registered in Firestore: {uid}")
            return response.FireBaseResponse(
                message="User registered successfully",
                data={"isNewUser": True, "isAnonymous": False}
            )
        else:
            # Update last login for returning users
            user_ref.update({
                "lastLogin": SERVER_TIMESTAMP,
                "name": name # Keep display name synced in case they changed it on Google
            })
            logger.info(f"Existing user logged in: {uid}")
            return response.FireBaseResponse(
                message="User login recorded",
                data={"isNewUser": False, "isAnonymous": False}
            )

    except Exception as e:
        logger.error(f"Failed to sync user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User sync failed: {e}"
        )