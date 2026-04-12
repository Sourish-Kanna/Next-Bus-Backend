from fastapi.testclient import TestClient
from main import app

# Create a TestClient instance to interact with the FastAPI app
client = TestClient(app)

def test_read_main():
    """
    Test the GET request to the root endpoint (/).
    It should return a 200 OK status code and a welcome message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}

def test_head_main():
    """
    Test the HEAD request to the root endpoint (/).
    It should return a 200 OK status code and no content body.
    """
    response = client.head("/")
    assert response.status_code == 200
    # A HEAD request shouldn't return a body
    assert response.text == ""
