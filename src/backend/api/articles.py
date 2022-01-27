from typing import List

from fastapi import APIRouter

from src.backend.db import db
from src.backend.db.SQLmodel import Article, ArticleGet, ArticleUpdate


router = APIRouter()


@router.get("/", response_model=List[Article])
def get_all_articles() -> List:
    return db.select_all_articles()


@router.patch("/read/{id}", response_model=ArticleGet)
def edit_article(id: int, article: ArticleUpdate):
    return db.update_article(id, article)


@router.post("/add")
def add_article(title: str, url: str, source: str, published_date: str, read: bool = False):
    db.insert_article(title=title, url=url, source=source, published_date=published_date, read=False)
