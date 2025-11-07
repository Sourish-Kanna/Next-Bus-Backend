from unittest.mock import patch, MagicMock
from google.api_core.exceptions import Conflict

@patch('v1.common.firebase.db')
def test_get_routes_success(mock_db, client):
    """Tests successfully getting all routes."""
    mock_route1 = MagicMock()
    mock_route1.id = "route1"
    mock_route2 = MagicMock()
    mock_route2.id = "route2"
    mock_db.collection.return_value.stream.return_value = [mock_route1, mock_route2]

    response = client.get("/v1/route/routes")

    assert response.status_code == 200
    assert response.json()["data"] == ["route1", "route2"]

@patch('v1.common.firebase.db')
@patch('v1.common.firebase.Name_and_UID')
def test_add_new_route_success(mock_name_and_uid, mock_db, client):
    """
    Tests the /v1/route/add endpoint successfully adding a route.
    The conftest.py mock for get_admin_details will fix the 401.
    """
    mock_name_and_uid.return_value = ("test_user", "test_uid")
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    response = client.post("/v1/route/add", json={
        "route_name": "test_route",
        "stops": ["stop1", "stop2"],
        "start": "start",
        "end": "end",
        "timing": {"time": "10:00", "stop_name": "start"}
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    mock_doc_ref.create.assert_called_once()

@patch('v1.common.firebase.db')
def test_add_new_route_conflict(mock_db, client):
    """
    Tests the /v1/route/add endpoint for a route that already exists.
    The conftest.py mock for get_admin_details will fix the 401.
    """
    mock_doc_ref = MagicMock()
    mock_doc_ref.create.side_effect = Conflict("Document already exists")
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    response = client.post("/v1/route/add", json={
        "route_name": "test_route",
        "stops": ["stop1", "stop2"],
        "start": "start",
        "end": "end",
        "timing": {"time": "10:00", "stop_name": "start"}
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 409

@patch('v1.common.firebase.db')
def test_get_routes_failure(mock_db, client):
    """Tests a server error when getting all routes."""
    mock_db.collection.return_value.stream.side_effect = Exception("DB error")

    response = client.get("/v1/route/routes")

    assert response.status_code == 500