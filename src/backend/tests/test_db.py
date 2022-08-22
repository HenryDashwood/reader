import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Source
from src.backend.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_source(client: TestClient):
    response = client.post("/sources/add", json={"url": "https://wayofthedodo.substack.com/feed"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "The Way Of The Dodo"
    assert data["url"] == "https://wayofthedodo.substack.com/feed"
    assert data["id"] is not None


def test_read_source(session: Session, client: TestClient):
    source = Source(name="The Way Of The Dodo", url="https://wayofthedodo.substack.com/feed")
    session.add(source)
    session.commit()

    response = client.get(f"/sources/{source.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == source.name
    assert data["url"] == source.url
    assert data["id"] == source.id
