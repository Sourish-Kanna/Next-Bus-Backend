from fastapi import APIRouter, HTTPException, status, Depends
import v1.common.response_base as response_base
from v1.common.decorators import verify_id_token, log_activity
import v1.common.firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
test_router = APIRouter(prefix="/test", tags=["Test"])
 
@test_router.get("/user")
@verify_id_token
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

@test_router.post("/verify_token", response_model=response_base.FireBaseResponse)
@verify_id_token
@log_activity
def verify_firebase_token(token: str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    """Verify Firebase ID token."""
    try:
        decoded_token = firebase.auth.verify_id_token(token)
        logger.info("Token verified successfully in /test-done/verify_token endpoint.")
        return response_base.FireBaseResponse(
            message="Token is valid",
            data={
                "token_details": decoded_token
            },
        )
    except Exception as e:
        logger.error(f"Token verification failed in /test-done/verify_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )

@test_router.get("/{route_name}")
@log_activity
def get_route_details(route_name: str) -> response_base.FireBaseResponse:
    """
    Get all details for a given route.
    """
    try:
        logger.info(f"Fetching details for route: {route_name}")
        doc_ref = firebase.db.collection("busRoutes").document(route_name)
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Route '{route_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route '{route_name}' not found"
            )
        logger.info(f"Route details fetched successfully for {route_name}")
        return response_base.FireBaseResponse(
            message="Route details fetched successfully",
            data=doc.to_dict() # type: ignore
        )
    except Exception as e:
        logger.error(f"Failed to fetch route details for {route_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch route details: {e}"
        )
   
