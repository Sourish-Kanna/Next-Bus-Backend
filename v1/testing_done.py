import v1.common_response_base as response_base
from fastapi import HTTPException, status, APIRouter, Depends
from v1.common_decorators import log_activity, verify_id_token
import v1.base_firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
test_done = APIRouter(prefix="/test-done", tags=["Test"])

@test_done.post("/verify_token", response_model=response_base.FireBaseResponse)
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