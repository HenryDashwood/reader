from typing import List

import feedparser
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.backend.config import PROJECT_FOLDER
from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Source, SourceBase, SourceRead, SourceReadWithArticles

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[Source])
def get_all_sources(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    current_user: User = Depends(get_current_user),
) -> List:
    statement = select(Source).offset(offset).limit(limit)
    results = session.exec(statement).all()
    return results


@router.get("/{source_id}", response_model=SourceRead)
def get_source(*, session: Session = Depends(get_session), source_id: int):
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/add", response_model=Source)
def add_source(*, session: Session = Depends(get_session), payload: SourceBase):
    try:
        statement = select(Source).where(Source.url == payload.url)
        source = session.exec(statement).first()
        if not source:
            if payload.name is None:
                feed = feedparser.parse(payload.url)
                source = Source(name=feed.feed.title, url=payload.url)
            else:
                source = Source(name=payload.name, url=payload.url)
            session.add(source)
            session.commit()
        source = session.exec(statement).first()
        return source
    except Exception as e:
        return


# def select_source_by_url(*, session: Session = Depends(get_session), url: str) -> Source:
#     statement = select(Source).where(Source.url == url)
#     result = session.exec(statement).first()
#     return result


def select_source_by_name(*, session: Session = Depends(get_session), name: str) -> Source:
    # statement = select(Source).where(Source.name == name)
    result = session.exec(select(Source).where(Source.name == name)).first()
    return result
