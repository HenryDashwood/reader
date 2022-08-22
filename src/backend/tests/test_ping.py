import pytest
from fastapi.testclient import TestClient

from src.backend.config import Settings, get_settings
from src.backend.main import app


client = TestClient(app)


@pytest.fixture(name="client")
def client_fixture():
    def get_settings_override():
        return Settings(testing=True)

    app.dependency_overrides[get_settings] = get_settings_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_ping(client: TestClient):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"environment": "dev", "ping": "pong", "testing": True}


# (capsys)
# with capsys.disabled():
#     print(os.environ.get("secret_key"))
