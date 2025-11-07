from unittest.mock import patch

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_success(mock_get_admin_details, client):
    """Tests successfully getting user details."""
    # This test overrides the conftest.py mock
    mock_get_admin_details.return_value = {"name": "test_user", "uid": "test_uid"}

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "test_user"

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_not_found(mock_get_admin_details, client):
    """
    Tests getting details for a non-existent user.
    The conftest.py mock will let the decorator pass.
    This test's local mock will override the conftest mock.
    """
    # This mock overrides the one in conftest.py for this test only
    mock_get_admin_details.return_value = None

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404

@patch('v1.common.firebase.get_admin_details')
def test_get_user_details_failure(mock_get_admin_details, client):
    """Tests a failure during user detail retrieval."""
    # This mock overrides the one in conftest.py for this test only
    mock_get_admin_details.side_effect = Exception("Invalid token")

    response = client.get("/v1/user/get-user-details", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 401