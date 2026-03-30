from fastapi.testclient import TestClient
from main import app
from tests.conftest import client

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]