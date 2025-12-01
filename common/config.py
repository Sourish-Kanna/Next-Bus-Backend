import os
import logging
from pathlib import Path
import dotenv

logger = logging.getLogger(__name__)


def load_env():
    """Load environment variables from dev.env or prod.env files.
    Priority is given to dev.env for local development.
    """
    dev_path = Path("dev.env")
    prod_path = Path("prod.env")
    if dev_path.exists():
        logger.info("dev.env found; loading dev.env for local development")
        dotenv.load_dotenv(dev_path)
        return
    elif prod_path.exists():
        logger.info("prod.env found; loading prod.env for environment variables")
        dotenv.load_dotenv(prod_path)
        return
    logger.info("No prod.env found; relying on host environment variables")

def get_env(key: str, default=None, required=False):
    """Centralized env getter.

    - Uses os.getenv under the hood.
    - If required and missing, raise ValueError.
    """
    val = os.getenv(key, default)
    if required and (val is None or val == ""):
        raise ValueError(f"Required environment variable '{key}' is not set")
    return val


def resolve_origins():
    """Parse `ORIGIN_LIST` into a list usable by `CORSMiddleware`.
    If the env is a single `*`, return ["*"]. If empty return [].
    """
    origin_list_str = os.getenv("ORIGIN_LIST")
    if origin_list_str == "*":
        return ["*"]
    return [origin.strip() for origin in origin_list_str.split(",") if origin.strip()]
