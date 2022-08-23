from sqlmodel import Session, SQLModel, create_engine

from src.backend.config import PROJECT_FOLDER


sqlite_url = f"sqlite:///{PROJECT_FOLDER}/data/database.db"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def init_db():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session
