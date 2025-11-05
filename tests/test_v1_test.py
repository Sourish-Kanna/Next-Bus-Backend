from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch('v1.common.firebase.get_token_details')
def test_verify_token_success(mock_get_token_details):
    mock_get_token_details.return_value = {"user_id": "test_user"}
    response = client.post("/v1/test/verify_token", headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 200
    assert response.json()["data"]["user_id"] == "test_user"

@patch('v1.common.firebase.get_token_details')
def test_verify_token_failure(mock_get_token_details):
    mock_get_token_details.side_effect = Exception("Invalid token")
    response = client.post("/v1/test/verify_token", headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 401
