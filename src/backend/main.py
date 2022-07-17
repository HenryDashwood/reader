import logging
from datetime import timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from .api import articles, ping, sources, updates, users
from .db.db import init_db


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


# @app.on_event("startup")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


@app.post("/token", response_model=users.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = users.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    app()
