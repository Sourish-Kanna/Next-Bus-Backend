def test_read_main(client):
    """
    Tests the main GET endpoint.
    The 'client' argument is now magically provided by conftest.py
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}

def test_head_main(client):
    """Tests the main HEAD endpoint."""
    response = client.head("/")
    assert response.status_code == 200

def test_favicon(client):
    """Tests the favicon endpoint."""
    response = client.get("/favicon.ico")
    assert response.status_code == 204