from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from src.backend.db.db import get_session
from src.backend.db.SQLmodel import Update

from .users import User, get_current_user


router = APIRouter()


@router.get("/", response_model=List[Update])
def get_all_updates(
    *, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)
) -> List:
    statement = select(Update)
    results = session.exec(statement)
    return results.all()


@router.get("/latest", response_model=str)
def get_last_update(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> str:
    statement = select(Update).order_by(Update.timestamp.desc())
    results = session.exec(statement)
    first_result = results.first()
    if first_result:
        return first_result.timestamp
    else:
        return "Never"


def create_update(
    *, session: Session = Depends(get_session), timestamp: str, current_user: User = Depends(get_current_user)
):
    try:
        update = Update(timestamp=timestamp)
        session.add(update)
        session.commit()
    except Exception as e:
        print(e)
