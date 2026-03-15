from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_me_page():
    response = client.get("/user/me-page")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
