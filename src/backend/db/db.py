from pathlib import Path
from typing import List

import feedparser
from dateutil import parser
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from .SQLmodel import Article, ArticleUpdate, Source, Update, User


PARENT_DIR = Path(__file__).parent.parent.parent.parent.resolve()


sqlite_file_name = f"{PARENT_DIR}/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def init_db(populate=False):
    create_db_and_tables()
    if populate:
        populate_sources_table_from_file()


def get_session():
    with Session(engine) as session:
        yield session


# Articles


def select_all_articles(offset, limit, session: Session) -> List:
    statement = select(Article).order_by(Article.published_date.desc()).offset(offset).limit(limit)
    results = session.exec(statement).all()
    return results


def select_article(article_id: int):
    with Session(engine) as session:
        article = session.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article


def insert_article(title: str, url: str, source: Source, published_date: str, read: bool = False):
    try:
        with Session(engine) as session:
            existing_article = session.exec(select(Article).where(Article.url == url)).first()
            if existing_article:
                return
            published_date = parser.parse(published_date).strftime("%Y-%m-%d %H:%M:%S")
            article = Article(title=title, url=url, published_date=published_date, read=read)
            article.source = source
            session.add(article)
            session.commit()
    except Exception as e:
        print(e)
        return


def update_article(id: int, new_article: ArticleUpdate):
    with Session(engine) as session:
        db_article = session.get(Article, id)
        if not db_article:
            raise HTTPException(status_code=404, detail="Article not found")
        for key, value in new_article.dict(exclude_unset=True).items():
            setattr(db_article, key, value)
        session.add(db_article)
        session.commit()
        session.refresh(db_article)
        return db_article


# Updates


def select_all_updates() -> List:
    with Session(engine) as session:
        statement = select(Update)
        results = session.exec(statement)
        return results.all()


def select_last_update() -> str:
    with Session(engine) as session:
        statement = select(Update).order_by(Update.timestamp.desc())
        results = session.exec(statement)
        first_result = results.first()
        if first_result:
            return first_result.timestamp
        else:
            return "Never"


def insert_update(current_time: str) -> None:
    try:
        update = Update(timestamp=current_time)
        with Session(engine) as session:
            session.add(update)
            session.commit()
    except Exception as e:
        print(e)


# Users


def select_all_users() -> List:
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement)
        return results.all()


def insert_user(username: str, hashed_password: str) -> None:
    try:
        user = User(email=username, hashed_password=hashed_password)
        with Session(engine) as session:
            session.add(user)
            session.commit()
    except Exception as e:
        print(e)


# Sources


def select_source(source_id: int):
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source


def select_source_by_url(url: str) -> Source:
    with Session(engine) as session:
        statement = select(Source).where(Source.url == url)
        result = session.exec(statement).first()
        return result


def select_source_by_name(name: str) -> Source:
    with Session(engine) as session:
        statement = select(Source).where(Source.name == name)
        result = session.exec(statement).first()
        return result


def insert_source(name: str = "", url: str = "", users: List[User] = []):
    try:
        source = select_source_by_url(url)
        if not source:
            if name == "":
                feed = feedparser.parse(url)
                name = feed.feed.title
            source = Source(name=name, url=url)
            with Session(engine) as session:
                session.add(source)
                session.commit()
        source = select_source_by_url(url)
        return source.json()
    except Exception as e:
        return


def select_all_sources(offset: int = None, limit: int = None) -> List:
    with Session(engine) as session:
        statement = select(Source).offset(offset).limit(limit)
        results = session.exec(statement).all()
        return results


def populate_sources_table_from_file():
    import json

    from rich.live import Live
    from rich.table import Table

    table = Table("Name", "URL")
    with Live(table, refresh_per_second=4, transient=True):
        with open(f"{PARENT_DIR}/data/feeds.txt") as f:
            for line in f:
                source = insert_source(url=line.strip())
                if source:
                    source = json.loads(source)
                    table.add_row(source["name"], source["url"])
