from fastapi import APIRouter, HTTPException, status, Depends
import common.response_base as response_base
from common.decorators import verify_id_token, log_activity
import common.firebase as firebase
import common as common
import logging

logger = logging.getLogger(__name__)
test_router = APIRouter(prefix="/test", tags=["Test"])


@test_router.post("/verify_token", response_model=response_base.FireBaseResponse)
@verify_id_token
@log_activity
def verify_firebase_token(token: str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
    """Verify Firebase ID token."""
    try:
        decoded_token = firebase.get_token_details(token)
        logger.info("Token verified successfully in /test-done/verify_token endpoint.")
        return response_base.FireBaseResponse(
            message="Token is valid",
            data={
                "user_id": decoded_token.get("uid", ""),  # Changed from user_id to uid
            },
        )
    except Exception as e:
        logger.error(f"Token verification failed in /test-done/verify_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )