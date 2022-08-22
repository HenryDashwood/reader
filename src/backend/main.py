import logging
from datetime import timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .api import articles, ping, sources, updates, users
from .db.db import get_session, init_db


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PARENT_DIR = Path(__file__).parent.parent.parent.resolve()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)
    application.include_router(articles.router, prefix="/articles", tags=["articles"])
    application.include_router(sources.router, prefix="/sources", tags=["sources"])
    application.include_router(updates.router, prefix="/updates", tags=["updates"])
    application.include_router(users.router, prefix="/users", tags=["users"])
    application.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(populate=False)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


if __name__ == "__main__":
    app()
