from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserSourceLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    source_id: Optional[int] = Field(default=None, foreign_key="source.id", primary_key=True)


class SourceBase(SQLModel):
    name: str = Field(nullable=False)
    url: str = Field(nullable=False, sa_column_kwargs={"unique": True})


class Source(SourceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    users: List["User"] = Relationship(back_populates="sources", link_model=UserSourceLink)
    articles: List["Article"] = Relationship(back_populates="source")


class SourceGet(SourceBase):
    id: int


class ArticleBase(SQLModel):
    title: str = Field(nullable=False)
    url: str = Field(nullable=False, sa_column_kwargs={"unique": True})
    published_date: str = Field(nullable=False)
    read: bool = Field(default=False, nullable=False)
    source_id: Optional[int] = Field(default=None, foreign_key="source.id")


class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: Source = Relationship(back_populates="articles")


class ArticleCreate(ArticleBase):
    source_name: str = Field(nullable=False)


class ArticleGet(ArticleBase):
    id: int


class ArticleUpdate(SQLModel):
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    read: Optional[bool] = None


class ArticleReadWithSource(ArticleGet):
    source: Optional[SourceGet] = None


class SourceReadWithArticles(SourceGet):
    articles: List[ArticleGet] = []


class Update(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: str = Field(nullable=False, sa_column_kwargs={"unique": True})


class UserBase(SQLModel):
    email: str = Field(nullable=False, sa_column_kwargs={"unique": True})
    hashed_password: str = Field(nullable=False)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sources: List["Source"] = Relationship(back_populates="users", link_model=UserSourceLink)
