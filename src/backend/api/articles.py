from typing import List

from dateutil import parser
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Article, ArticleCreate, ArticleGet, ArticleGetWithSource, ArticleUpdate

from .sources import Source
from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[ArticleGetWithSource])
def get_all_articles(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: User = Depends(get_current_user),
) -> List[ArticleGetWithSource]:
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


@router.post("/add", response_model=ArticleGetWithSource)
def add_article(*, session: Session = Depends(get_session), payload: ArticleCreate) -> Article:
    existing_article = session.exec(select(Article).where(Article.url == payload.url)).first()
    if existing_article:
        return existing_article
    source = session.exec(select(Source).where(Source.name == payload.source_name)).first()
    source_id = source.id if source else None
    article = Article(
        title=payload.title,
        url=payload.url,
        published_date=parser.parse(payload.published_date).strftime("%Y-%m-%d %H:%M:%S"),
        read=payload.read,
        source_id=source_id,
    )
    session.add(article)
    session.commit()
    return session.exec(select(Article).where(Article.id == article.id)).first()
