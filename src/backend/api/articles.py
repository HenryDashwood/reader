from typing import List

from fastapi import APIRouter, Depends, Query

from src.backend.db import db
from src.backend.db.SQLmodel import Article, ArticleGet, ArticleUpdate

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[Article])
def get_all_articles(
    offset: int = 0, limit: int = Query(default=100, lte=100), current_user: User = Depends(get_current_user)
) -> List:
    return db.select_all_articles(offset, limit)


@router.get("/{article_id}", response_model=ArticleGet)
def get_article(article_id: int):
    return db.select_article(article_id)


@router.patch("/read/{id}", response_model=ArticleGet)
def edit_article(id: int, article: ArticleUpdate, current_user: User = Depends(get_current_user)):
    return db.update_article(id, article)


@router.post("/add")
def add_article(
    title: str,
    url: str,
    source: str,
    published_date: str,
    read: bool = False,
    current_user: User = Depends(get_current_user),
):
    db.insert_article(title=title, url=url, source=source, published_date=published_date, read=False)
