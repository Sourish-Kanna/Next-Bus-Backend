from unittest.mock import patch

def test_verify_token_success(client):
    """
    Tests successful token verification.
    conftest.py now mocks get_token_details, so this will pass.
    """
    response = client.post("/v1/test/verify_token", headers={"Authorization": "Bearer test_token"})
    
    # This assertion should now work
    assert response.status_code == 200
    assert response.json()["data"]["user_id"] == "test_user_uid_from_mock"

@patch('v1.common.firebase.get_token_details')
def test_verify_token_failure(mock_get_token_details, client):
    """Tests failed token verification."""
    # This test overrides the conftest mock to test the failure case.
    mock_get_token_details.side_effect = Exception("Invalid token")
    response = client.post("/v1/test/verify_token", headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 401