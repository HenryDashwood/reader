from typing import List

from fastapi import APIRouter, Path
from sqlmodel import Session, select

from src.backend.db import db
from src.backend.models.SQLmodel import Article, ArticleGet, ArticleUpdate


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


# @router.put("/{id}/", response_model=Article)
# async def update_article(payload: ArticleUpdatePayloadSchema, id: int = Path(..., gt=0)) -> Article:
#     summary = await crud.put(id, payload)
#     if not summary:
#         raise HTTPException(status_code=404, detail="Summary not found")

#     return summary

# def update_articles(engine):
#     with Session(engine) as session:
#         statement = select(Article).where(Article.name == "Spider-Boy")
#         results = session.exec(statement)
#         article = results.one()
#         article.age = 16
#         session.add(article)
#         session.commit()
#         session.refresh(article)
