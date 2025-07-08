from fastapi import APIRouter, HTTPException, status, Depends
import v1.common.response_base as response_base
from v1.common.decorators import log_activity
import v1.common.firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.get("/get-user-details")
@log_activity
def get_user_details(token: str = Depends(common.get_token_from_header)):
    """Get User Details"""
    try:
        logger.info("Fetching user details")
        detail = firebase.get_admin_details(token)
        if not detail:
            logger.warning("User details not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User details not found"
            )
        
        logger.info("User details fetched successfully")
        return response_base.FireBaseResponse(
            message="User details fetched successfully",
            data=detail,
        )
    except Exception as e:
        logger.error(f"Failed to fetch user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )
