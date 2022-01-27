from typing import Optional

from sqlmodel import Field, SQLModel


class ArticleBase(SQLModel):
    title: str = Field(nullable=False)
    url: str = Field(nullable=False, sa_column_kwargs={"unique": True})
    source: str = Field(nullable=False)
    published_date: str = Field(nullable=False)
    read: bool = Field(default=False, nullable=False)


class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ArticleCreate(ArticleBase):
    pass


class ArticleGet(ArticleBase):
    id: int


class ArticleUpdate(SQLModel):
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    read: Optional[bool] = None


class Update(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: str = Field(nullable=False, sa_column_kwargs={"unique": True})
