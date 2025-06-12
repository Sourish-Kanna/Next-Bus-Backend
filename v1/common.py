from datetime import datetime
from fastapi import HTTPException , status, Header
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def seconds_difference(t1: str, t2: str) -> int:
    fmt = "%I:%M %p"
    today = datetime.today().date()
    dt1 = datetime.combine(today, datetime.strptime(t1, fmt).time())
    dt2 = datetime.combine(today, datetime.strptime(t2, fmt).time())
    diff = (dt2 - dt1).total_seconds()
    logger.info(f"Calculated seconds difference between {t1} and {t2}: {diff}")
    return int(diff)

def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        logger.error("Invalid or missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header"
        )
    token = authorization.split(" ", 1)[1]
    logger.info("Extracted token from Authorization header")
    return token