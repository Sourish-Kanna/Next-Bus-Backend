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
from .auth import auth_router
from .test import test_router
from .firebase import firebase_router

# Importing routers from v1 module
ver_1 = APIRouter(prefix="/v1")
ver_1.include_router(auth_router)
ver_1.include_router(test_router)
ver_1.include_router(firebase_router)
