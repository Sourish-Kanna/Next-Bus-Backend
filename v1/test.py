from fastapi import APIRouter, HTTPException, status, Depends
import v1.common.response_base as response_base
from v1.common.decorators import verify_id_token, log_activity
import v1.common.firebase as firebase
import v1.common as common
import logging

logger = logging.getLogger(__name__)
test_router = APIRouter(prefix="/test", tags=["Test"])

@test_router.get("/{route_name}")
@log_activity
@verify_id_token
def get_route_details(route_name: str,token: str = Depends(common.get_token_from_header)) -> response_base.FireBaseResponse:
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
    
    