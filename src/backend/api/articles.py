from typing import List

from dateutil import parser
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Article, ArticleGet, ArticleReadWithSource, ArticleUpdate

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[ArticleReadWithSource])
def get_all_articles(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: User = Depends(get_current_user),
) -> List[ArticleReadWithSource]:
    statement = select(Article).order_by(Article.published_date.desc()).offset(offset).limit(limit)
    results = session.exec(statement).all()
    return results


@router.get("/{article_id}", response_model=ArticleGet)
def get_article(*, session: Session = Depends(get_session), article_id: int):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.patch("/read/{id}", response_model=ArticleGet)
def toggle_read(
    *,
    session: Session = Depends(get_session),
    id: int,
    article: ArticleUpdate,
    current_user: User = Depends(get_current_user),
):
    db_article = session.get(Article, id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    for key, value in article.dict(exclude_unset=True).items():
        setattr(db_article, key, value)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article


@router.post("/add")
def add_article(
    *,
    session: Session = Depends(get_session),
    title: str,
    url: str,
    source: str,
    published_date: str,
    read: bool = False,
    current_user: User = Depends(get_current_user),
):
    try:
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
