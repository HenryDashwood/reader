from typing import List

from fastapi import APIRouter, Depends, Query

from src.backend.db import db
from src.backend.db.SQLmodel import Source, SourceRead, SourceReadWithArticles

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[Source])
def get_all_sources(
    offset: int = 0, limit: int = Query(default=100, lte=100), current_user: User = Depends(get_current_user)
) -> List:
    return db.select_all_sources(offset, limit)


@router.get("/{source_id}", response_model=SourceRead)
def get_source(source_id: int):
    return db.select_source(source_id)


@router.get("/{source_id}", response_model=SourceReadWithArticles)
def get_source_with_articles(source_id: int):
    return db.select_source_with_articles(source_id)
