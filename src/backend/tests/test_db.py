from typing import Dict

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


@pytest.fixture(name="auth")
def auth_fixture(client: TestClient):
    response = client.post("/users/register", data={"username": "hcndashwood@gmail.com", "password": "nelson"})
    response = client.post(f"/users/token", data={"username": "hcndashwood@gmail.com", "password": "nelson"})
    auth = response.json()
    yield auth


def test_create_source(client: TestClient, auth: Dict[str, str]):
    response = client.post(
        "/sources/add",
        json={"url": "https://wayofthedodo.substack.com/feed"},
        headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"},
    )
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


def test_create_article(session: Session, client: TestClient, auth: Dict[str, str]):
    source = Source(name="The Way Of The Dodo", url="https://wayofthedodo.substack.com/feed")
    session.add(source)
    session.commit()

    response = client.post(
        "/articles/add",
        json={
            "title": "All This Useless Beauty",
            "url": "https://wayofthedodo.substack.com/p/all-this-useless-beauty",
            "published_date": "Sun, 26 Sep 2021 19:36:11",
            "read": False,
            "source_name": "The Way Of The Dodo",
        },
        headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "All This Useless Beauty"
    assert data["url"] == "https://wayofthedodo.substack.com/p/all-this-useless-beauty"
    assert data["published_date"] == "2021-09-26 19:36:11"
    assert data["source_id"] is not None
    assert data["id"] is not None
    assert data["source"]["id"] is not None
    assert data["source"]["name"] == "The Way Of The Dodo"
    assert data["source"]["url"] == "https://wayofthedodo.substack.com/feed"
    assert data["id"] == data["source"]["id"]
