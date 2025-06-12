import v1.test as test
import v1.common_response_base as response_base
from fastapi import Body, HTTPException, status, APIRouter
import v1.common_response_base as response_base
import v1.base_firebase as firebase

test_done = APIRouter(prefix="/test-done", tags=["Test"])

@test_done.post("/verify_token", response_model=response_base.FireBaseResponse)
# @verify_id_token
# @log_activity
def verify_firebase_token(input: response_base.TokenRequest = Body(...)) -> response_base.FireBaseResponse:
    """Verify Firebase ID token."""
    try:
        decoded_token = firebase.auth.verify_id_token(input.token)
        return response_base.FireBaseResponse(
            message="Token is valid",
            data={
                "token_details": decoded_token
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}"
        )