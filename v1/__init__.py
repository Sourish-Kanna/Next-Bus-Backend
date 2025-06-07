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
from .timmings import routes_timming_router
import os  # Import os to read environment variables

# Importing routers from v1 module
ver_1 = APIRouter(prefix="/v1")

ver_1.include_router(routes_timming_router)



# Conditionally include the test_router based on the environment variable
if os.getenv("ENABLE_TEST_ROUTE", "false").lower() == "true":
    ver_1.include_router(test_router)

