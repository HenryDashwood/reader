from sqlmodel import Session, SQLModel, create_engine

from src.backend.config import PROJECT_FOLDER


sqlite_url = f"sqlite:///{PROJECT_FOLDER}/data/database.db"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def init_db(populate=False):
    create_db_and_tables()
    if populate:
        populate_sources_table_from_file()


def get_session():
    with Session(engine) as session:
        yield session


# def select_source_by_url(*, session: Session = Depends(get_session), url: str) -> Source:
#     statement = select(Source).where(Source.url == url)
#     result = session.exec(statement).first()
#     return result


# def select_source_by_name(*, session: Session = Depends(get_session), name: str) -> Source:
#     statement = select(Source).where(Source.name == name)
#     result = session.exec(statement).first()
#     return result


def populate_sources_table_from_file():
    import json

    from rich.live import Live
    from rich.table import Table

    table = Table("Name", "URL")
    with Live(table, refresh_per_second=4, transient=True):
        with open(f"{PROJECT_FOLDER}/data/feeds.txt") as f:
            for line in f:
                source = insert_source(url=line.strip())
                if source:
                    source = json.loads(source)
                    table.add_row(source["name"], source["url"])
