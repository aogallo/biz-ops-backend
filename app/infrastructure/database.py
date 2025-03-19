# DB Connection: Uses SQLAlchemy asnc engine
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
import os

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+asyncpg://user:password@localhost:5432/mydb"
)

engine = create_engine(DATABASE_URI, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


async def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
