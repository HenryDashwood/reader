from pathlib import Path
from typing import List

import pandas as pd
import requests
from fastapi import HTTPException
from requests_html import HTMLSession
from sqlmodel import Session, SQLModel, create_engine, select

from .SQLmodel import Article, ArticleUpdate, Source, Update, User


PARENT_DIR = Path(__file__).parent.parent.parent.parent.resolve()


sqlite_file_name = f"{PARENT_DIR}/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})


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
    print(results)
    return results


def select_article(article_id: int):
    with Session(engine) as session:
        article = session.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article


def insert_article(title: str, url: str, source: Source, published_date: str, read: bool = False):
    try:
        article = Article(title=title, url=url, published_date=published_date, read=read)
        article.source = source
        with Session(engine) as session:
            session.add(article)
            session.commit()
    except Exception as e:
        return


def update_article(id: int, article: ArticleUpdate):
    with Session(engine) as session:
        db_article = session.get(Article, id)
        if not db_article:
            raise HTTPException(status_code=404, detail="Article not found")
        new_article_data = article.dict(exclude_unset=True)
        for key, value in new_article_data.items():
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
        results = session.exec(statement).first()
        return results


def insert_source(name: str, url: str, users: List[User] = []):
    try:
        existing_source = select_source_by_url(url)
        if not existing_source:
            source = Source(name=name, url=url)
            with Session(engine) as session:
                session.add(source)
                session.commit()
    except Exception as e:
        return


def select_all_sources(offset: int = None, limit: int = None) -> List:
    with Session(engine) as session:
        statement = select(Source).offset(offset).limit(limit)
        results = session.exec(statement).all()
        return results


def populate_sources_table_from_file():
    with open(f"{PARENT_DIR}/data/feeds.txt") as f:
        for line in f:
            insert_source(engine, timestamp=line.strip())
