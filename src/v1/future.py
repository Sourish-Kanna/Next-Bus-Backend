from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import common.firebase as firebase
import common as common
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def save_historical_data(route_name: str, reported_time: str, official_time: str, delay: float, user_id: str):
    """
    Saves the raw individual report to 'historicalData' for future ML training.
    """
    try:
        now = datetime.now()        
        firebase.db.collection("historicalData").add({
            "timestamp": SERVER_TIMESTAMP,
            "dayOfWeek": now.weekday(), # 0=Monday, 6=Sunday
            "hourOfDay": now.hour,
            "route": route_name,
            "reportedTime": reported_time,
            "officialTime": official_time,
            "calculatedDelay": delay,
            "userId": user_id
        })
        logger.info(f"Historical data saved for route '{route_name}' by user '{user_id}'.")
    except Exception as e:
        logger.error(f"Failed to save historical data: {e}")

def isRateLimitExceeded(token:str, route_name:str, table:str) -> bool:
        """
        Checks if the user has updated the same route within the last minute.
        """
        name, uid = firebase.Name_and_UID(token)
        doc_ref = firebase.db.collection(table).document(route_name)
        doc = doc_ref.get()
        doc_dict = doc.to_dict()
        last_updated_by = doc_dict.get("lastUpdatedBy", "") # type: ignore
        last_updated_ts = doc_dict.get("lastUpdated") # type: ignore
        
        if f"{name} ({uid})" == last_updated_by and last_updated_ts:
            now = datetime.now(timezone.utc)                            
            diff = (now - last_updated_ts).total_seconds()
            
            if diff < 60:
                # firebase.log_to_firestore("RATE_LIMIT_HIT", {"route": input.route_name}, uid, "WARNING")
                logger.warning(f"Rate limit hit for user {uid} on route {route_name}")
                return True
        return False