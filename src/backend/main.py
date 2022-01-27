import json
from pathlib import Path

import logging

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import ping, articles, updates
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
    # init_db()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


# def get_data():
#     df = pd.read_csv(f"{PARENT_DIR}/data/latest.csv")
#     df.to_json(f"{PARENT_DIR}/data/latest.json", orient="records")
#     with open(f"{PARENT_DIR}/data/latest.json") as f:
#         data = json.load(f)
#         return data


# def get_last_update():
#     try:
#         with open(f"{PARENT_DIR}/data/updates.txt", "r") as f:
#             lines = f.read().splitlines()
#             last_line = lines[-1]
#             return last_line
#     except Exception as e:
#         print(e)
#         return "undefined"


# @app.post("/read")
# def mark_as_read():
#     pass


# @app.get("/")
# def root():
#     data = get_data_from_db()
#     last_update = get_last_update()
#     return {"data": data, "last_update": last_update}


if __name__ == "__main__":
    app()
