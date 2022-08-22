import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.config import Settings, get_settings
from src.backend.db.db import get_session
from src.backend.db.SQLmodel import User


router = APIRouter()

# to get a string like this run openssl rand -hex 32


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoginUser(BaseModel):
    username: str | None = None


class LoginUserInDB(LoginUser):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, session):
    users = session.exec(select(User))
    for user in users:
        if user.email == username:
            user_dict = {"username": user.email, "hashed_password": user.hashed_password}
            return LoginUserInDB(**user_dict)


def authenticate_user(username: str, password: str, session):
    user = get_user(username=username, session=session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(settings: Settings, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=LoginUser)
async def read_users_me(current_user: LoginUser = Depends(get_current_user)):
    return {"username": current_user.username}


@router.post("/register")
async def register(*, session: Session = Depends(get_session), username: str = Form(), password: str = Form()):
    errors = []
    if not username.__contains__("@"):
        errors.append("Valid email required")
    if len(password) < 6:
        errors.append("Password too short")
    if not errors:
        hashed_password = get_password_hash(password)
        try:
            user = User(email=username, hashed_password=hashed_password)
            session.add(user)
            session.commit()
        except Exception as e:
            print(e)
        return {"registered": "true"}
    return {"errors": errors}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
):
    user = authenticate_user(username=form_data.username, password=form_data.password, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(settings, data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
