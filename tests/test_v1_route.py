from unittest.mock import patch, MagicMock
from v1.common.response_base import Add_New_Route

@patch('v1.common.firebase.db')
@patch('v1.common.firebase.Name_and_UID')
def test_firebase_add_new_route_success(mock_name_and_uid, mock_db):
    """Tests the internal route creation logic successfully."""
    mock_name_and_uid.return_value = ("test_user", "test_uid")
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value.exists = False
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    from v1.route import firebase_add_new_route

    input_data = Add_New_Route(
        route_name="test_route",
        stops=["stop1", "stop2"],
        start="start",
        end="end",
        timing={"time": "10:00", "stop_name": "start"} 
    )

    response = firebase_add_new_route(input_data, "test_token")

    assert response.message == "Document created successfully with initial timing"
    mock_doc_ref.set.assert_called_once()

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
    mock_doc_ref.get.return_value.exists = False
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    response = client.post("/v1/route/add", json={
        "route_name": "test_route",
        "stops": ["stop1", "stop2"],
        "start": "start",
        "end": "end",
        "timing": {"time": "10:00", "stop_name": "start"}
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    mock_doc_ref.set.assert_called_once()

@patch('v1.common.firebase.db')
def test_add_new_route_conflict(mock_db, client):
    """
    Tests the /v1/route/add endpoint for a route that already exists.
    The conftest.py mock for get_admin_details will fix the 401.
    """
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value.exists = True
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