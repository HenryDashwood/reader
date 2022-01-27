import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import articles, ping, updates
from .db.db import init_db


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PARENT_DIR = Path(__file__).parent.parent.parent.resolve()


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)
    application.include_router(articles.router, prefix="/articles", tags=["articles"])
    application.include_router(updates.router, prefix="/updates", tags=["updates"])
    application.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


if __name__ == "__main__":
    app()
