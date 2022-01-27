from pydantic import BaseModel, AnyHttpUrl


class ArticlePayloadSchema(BaseModel):
    url: AnyHttpUrl


class ArticleResponseSchema(ArticlePayloadSchema):
    id: int


class ArticleUpdatePayloadSchema(ArticlePayloadSchema):
    summary: str
