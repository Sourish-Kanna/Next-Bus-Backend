from fastapi import APIRouter, HTTPException, status, Depends
import common.response_base as response_base
from common.decorators import log_activity
import common.firebase as firebase
import common as common
import logging

logger = logging.getLogger(__name__)
user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.get("/get-user-details")
@log_activity
def get_user_details(token: str = Depends(common.get_token_from_header)):
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
        
        return response_base.FireBaseResponse(
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