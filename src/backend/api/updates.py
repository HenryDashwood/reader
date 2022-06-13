from typing import List

from fastapi import APIRouter, Depends

from src.backend.db import db
from src.backend.db.SQLmodel import Update

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[Update])
def get_all_updates(current_user: User = Depends(get_current_user)) -> List:
    return db.select_all_updates()


@router.get("/latest", response_model=str)
def get_last_update(current_user: User = Depends(get_current_user)) -> str:
    return db.select_last_update()


def create_update(timestamp: str, current_user: User = Depends(get_current_user)):
    db.insert_update(timestamp)
