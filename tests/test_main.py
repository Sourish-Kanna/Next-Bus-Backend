from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}

def test_head_main():
    response = client.head("/")
    assert response.status_code == 200

def test_favicon():
    response = client.get("/favicon.ico")
    assert response.status_code == 204
