'''
This file initializes the version 1 API module for the Next-Bus Backend project.
It sets up the main API router for version 1 and includes sub-routers for:
- Authentication endpoints (login, registration, etc.)
- Testing endpoints (for health checks or diagnostics)
- Firebase-related endpoints (for push notifications or data sync)

All endpoints under this module are accessible with the `/v1` prefix.
'''

__version__ = "1.0.0"

from fastapi import APIRouter
from .test import test_router
from .time import timing_router
from .route import routes_router
from .user import user_router
import os
from common.config import get_env

# Importing routers from v1 module
ver_1 = APIRouter(prefix="/v1")

ver_1.include_router(timing_router)
ver_1.include_router(routes_router)
ver_1.include_router(user_router)

# Conditionally include the test_router based on the environment variable
if get_env("DEV_ENV", "false") == "true" or os.getenv("PYTEST_CURRENT_TEST"):
    ver_1.include_router(test_router)
