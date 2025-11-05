from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch('v1.common.firebase.db')
def test_get_time_success(mock_db):
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value.exists = True
    mock_doc_ref.get.return_value.to_dict.return_value = {
        "timing": [
            {"time": "10:00", "stop_name": "stop1", "delay_by": 0},
            {"time": "10:15", "stop_name": "stop2", "delay_by": 0},
        ]
    }
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    response = client.get("/v1/timings/test_route")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

@patch('v1.common.firebase.db')
def test_get_time_not_found(mock_db):
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value.exists = False
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    response = client.get("/v1/timings/test_route")

    assert response.status_code == 404

@patch('v1.time.firebase_update_time')
@patch('v1.time.firebase_add_new_time')
@patch('v1.common.decorators.verify_id_token', lambda func: func)
@patch('v1.common.decorators.is_authenticated', lambda func: func)
def test_update_time_update_existing(mock_add, mock_update):
    with patch('v1.common.firebase.db') as mock_db:
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {
            "timing": [
                {"time": "10:00", "stop_name": "stop1", "delay_by": 0, "deviation_sum": 0, "deviation_count": 0},
            ]
        }
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        response = client.post("/v1/timings/update", json={
            "route_name": "test_route",
            "timing": "10:01",
            "stop": "stop1"
        }, headers={"Authorization": "Bearer test_token"})

        assert response.status_code == 200
        mock_update.assert_called_once()
        mock_add.assert_not_called()

@patch('v1.time.firebase_update_time')
@patch('v1.time.firebase_add_new_time')
@patch('v1.common.decorators.verify_id_token', lambda func: func)
@patch('v1.common.decorators.is_authenticated', lambda func: func)
def test_update_time_add_new(mock_add, mock_update):
    with patch('v1.common.firebase.db') as mock_db:
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {
            "RouteName": "test_route",
            "timing": [
                {"time": "10:00", "stop_name": "stop1", "delay_by": 0, "deviation_sum": 0, "deviation_count": 0},
            ]
        }
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        response = client.post("/v1/timings/update", json={
            "route_name": "test_route",
            "timing": "11:00",
            "stop": "stop2"
        }, headers={"Authorization": "Bearer test_token"})

        assert response.status_code == 200
        mock_add.assert_called_once()
        mock_update.assert_not_called()
