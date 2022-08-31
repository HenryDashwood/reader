from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Article, Source
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


def test_read_source(session: Session, client: TestClient, auth: Dict[str, str]):
    source = Source(name="The Way Of The Dodo", url="https://wayofthedodo.substack.com/feed")
    session.add(source)
    session.commit()

    response = client.get(
        f"/sources/{source.id}", headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"}
    )
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
    assert data["source"] is not None
    assert data["source"]["id"] is not None
    assert data["source"]["name"] == "The Way Of The Dodo"
    assert data["source"]["url"] == "https://wayofthedodo.substack.com/feed"
    assert data["id"] == data["source"]["id"]


def test_get_all_articles(session: Session, client: TestClient, auth: Dict[str, str]):
    source1 = Source(name="The Way Of The Dodo", url="https://wayofthedodo.substack.com/feed")
    source2 = Source(name="Nintil", url="https://nintil.com/rss.xml")
    session.add(source1)
    session.add(source2)
    session.commit()
    source1 = session.exec(select(Source).where(Source.name == source1.name)).first()
    source2 = session.exec(select(Source).where(Source.name == source2.name)).first()

    article1 = Article(
        title="All This Useless Beauty",
        url="https://wayofthedodo.substack.com/p/all-this-useless-beauty",
        published_date="2021-09-26 19:36:11",
        read=False,
        source_id=source1.id,
    )
    session.add(article1)
    article2 = Article(
        title="Set Sail For Fail? On AI risk",
        url="https://nintil.com/ai-safety/",
        published_date="2022-08-04 00:00:00",
        read=False,
        source_id=source2.id,
    )
    session.add(article2)
    session.commit()

    response = client.get(
        "/articles/",
        data={"offset": 0, "limit": 100},
        headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"},
    )
    data = response.json()

    assert response.status_code == 200

    assert data[1]["title"] == "All This Useless Beauty"
    assert data[1]["url"] == "https://wayofthedodo.substack.com/p/all-this-useless-beauty"
    assert data[1]["published_date"] == "2021-09-26 19:36:11"
    assert data[1]["source_id"] is not None
    assert data[1]["id"] is not None
    assert data[1]["source"] is not None
    assert data[1]["source"]["id"] is not None
    assert data[1]["source"]["name"] == "The Way Of The Dodo"
    assert data[1]["source"]["url"] == "https://wayofthedodo.substack.com/feed"
    assert data[1]["id"] == data[1]["source"]["id"]

    assert data[0]["title"] == "Set Sail For Fail? On AI risk"
    assert data[0]["url"] == "https://nintil.com/ai-safety/"
    assert data[0]["published_date"] == "2022-08-04 00:00:00"
    assert data[0]["source_id"] is not None
    assert data[0]["source"] is not None
    assert data[0]["id"] is not None
    assert data[0]["source"]["id"] is not None
    assert data[0]["source"]["name"] == "Nintil"
    assert data[0]["source"]["url"] == "https://nintil.com/rss.xml"
    assert data[0]["id"] == data[0]["source"]["id"]


def test_toggle_article_read(session: Session, client: TestClient, auth: Dict[str, str]):
    source = Source(name="The Way Of The Dodo", url="https://wayofthedodo.substack.com/feed")
    session.add(source)
    session.commit()
    source = session.exec(select(Source).where(Source.name == source.name)).first()

    article = Article(
        title="All This Useless Beauty",
        url="https://wayofthedodo.substack.com/p/all-this-useless-beauty",
        published_date="2021-09-26 19:36:11",
        read=False,
        source_id=source.id,
    )
    session.add(article)
    session.commit()
    article = session.exec(select(Article).where(Article.url == article.url)).first()

    response = client.patch(
        f"/articles/read/{article.id}",
        json={
            "title": article.title,
            "url": article.url,
            "published_date": article.published_date,
            "read": True,
            "source_id": article.source_id,
        },
        headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == article.title
    assert data["url"] == article.url
    assert data["published_date"] == article.published_date
    assert data["read"] == True
    assert data["source_id"] == article.source_id
    assert data["id"] == article.id
