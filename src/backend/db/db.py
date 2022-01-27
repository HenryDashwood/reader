from asyncore import read
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select, or_, col

from src.backend.models.SQLmodel import Article, ArticleUpdate, Update
from src.backend.api import articles, updates


PARENT_DIR = Path(__file__).parent.parent.parent.parent.resolve()


sqlite_file_name = f"{PARENT_DIR}/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def populate_articles_table_from_file():
    df = pd.read_csv(f"{PARENT_DIR}/data/latest.csv")
    for i in range(df.shape[0]):
        insert_article(df.iloc[i]["title"], df.iloc[i]["link"], df.iloc[i]["source"], df.iloc[i]["pubDate"])


def populate_updates_table_from_file():
    with open(f"{PARENT_DIR}/data/updates.txt") as f:
        for line in f:
            updates.create_update(engine, timestamp=line.strip())


def init_db():
    create_db_and_tables()
    populate_articles_table_from_file()
    populate_updates_table_from_file()


def select_all_articles() -> List:
    with Session(engine) as session:
        statement = select(Article)
        results = session.exec(statement)
        return results.all()


def insert_article(title: str, url: str, source: str, published_date: str, read: bool = False):
    article = Article(title=title, url=url, source=source, published_date=published_date, read=read)
    with Session(engine) as session:
        session.add(article)
        session.commit()


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


def select_all_updates() -> List:
    with Session(engine) as session:
        statement = select(Update)
        results = session.exec(statement)
        return results.all()


def select_last_update() -> str:
    with Session(engine) as session:
        statement = select(Update).order_by(Update.timestamp.desc())
        results = session.exec(statement)
        latest_timestamp = results.first().timestamp
        return latest_timestamp


if __name__ == "__main__":
    init_db()
