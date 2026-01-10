from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

#Обратите внимание, что тестирующая функция является обычной def, а не асинхронной async def.
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.request == {"request"}