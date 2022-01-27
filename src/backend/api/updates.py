from typing import List

from fastapi import APIRouter, HTTPException, Path
from sqlmodel import Session, select

from src.backend.db import db
from src.backend.models.SQLmodel import Update


router = APIRouter()


@router.get("/", response_model=List[Update])
def get_all_updates() -> List:
    return db.select_all_updates()


@router.get("/latest", response_model=str)
def get_last_update() -> str:
    return db.select_last_update()


def create_update(engine, timestamp: str):
    article = Update(timestamp=timestamp)
    with Session(engine) as session:
        session.add(article)
        session.commit()
