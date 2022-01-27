from typing import List

from fastapi import APIRouter

from src.backend.db import db
from src.backend.db.SQLmodel import Update


router = APIRouter()


@router.get("/", response_model=List[Update])
def get_all_updates() -> List:
    return db.select_all_updates()


@router.get("/latest", response_model=str)
def get_last_update() -> str:
    return db.select_last_update()


def create_update(timestamp: str):
    db.insert_update(timestamp)
