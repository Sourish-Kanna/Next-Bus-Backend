import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

@pytest.fixture(scope="session")
def client():
    """
    Provides a TestClient for the app, with Firebase initialization 
    and authentication functions globally mocked.
    """
    
    # Define our mock payloads
    mock_token_payload = {
        "uid": "test_user_uid_from_mock",
        "name": "Test User",
        "email": "test@example.com",
        "firebase": {"sign_in_provider": "google.com"}
    }
    
    mock_admin_details_payload = {
        "isAdmin": True,
        "isLoggedIn": True,
        "isGuest": False,
        "sign_in_provider": "google.com",
    }

    # We need to mock verify_token as well since decorators use it directly
    with patch("v1.common.firebase.initialize_firebase") as mock_init, \
         patch("v1.common.firebase.verify_token") as mock_verify, \
         patch("v1.common.firebase.get_token_details", return_value=mock_token_payload) as mock_get_token, \
         patch("v1.common.firebase.get_admin_details", return_value=mock_admin_details_payload) as mock_get_admin:
        
        # Now that mocks are active, we can safely import the app
        # When running tests, ensure the app loads development routes
        os.environ["DEV_ENV"] = "true"  # ensure test routes are included
        from main import app
        
        # Yield the client for the tests to use
        with TestClient(app) as test_client:
            # debug: what routes are registered
            yield test_client