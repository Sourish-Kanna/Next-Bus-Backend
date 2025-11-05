from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_success(mock_get_admin_details):
    mock_get_admin_details.return_value = {"name": "test_user", "uid": "test_uid"}

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "test_user"

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_not_found(mock_get_admin_details):
    mock_get_admin_details.return_value = None

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_failure(mock_get_admin_details):
    mock_get_admin_details.side_effect = Exception("Invalid token")

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 401
