import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from urllib.request import Request

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.backend.db import db
from src.backend.db.SQLmodel import User


router = APIRouter()

PROJECT_FOLDER = Path(__file__).parent.parent.parent.parent.resolve()
load_dotenv(dotenv_path=PROJECT_FOLDER / ".env")

# to get a string like this run openssl rand -hex 32
SECRET_KEY = os.getenv("secret_key")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str | None = None


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    users = db.select_all_users()
    for user in users:
        if user.email == username:
            user_dict = {"username": user.email, "hashed_password": user.hashed_password}
            return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}


@router.post("/register")
async def register(username: str = Form(), password: str = Form()):
    errors = []
    if not username.__contains__("@"):
        errors.append("Valid email required")
    if len(password) < 6:
        errors.append("Password too short")
    if not errors:
        hashed_password = get_password_hash(password)
        db.insert_user(username=username, hashed_password=hashed_password)
        return {"registered": "true"}
    return {"errors": errors}


@router.patch("/add_feed")
async def add_feed(
    url: str = Form(),
    source: str = Form(),
    published_date: str = Form(),
    current_user: User = Depends(get_current_user),
):
    db.insert_feed(url=url, source=source, published_date=published_date, read=False)
    return {"added": "true"}
