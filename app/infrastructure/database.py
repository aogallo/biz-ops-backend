# DB Connection: Uses SQLAlchemy asnc engine
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
import os

# postgresql+asyncpg://user:password@localhost:5432/mydb
DATABASE_URI = os.getenv("DATABASE_URI", "")

if DATABASE_URI == "":
    raise Exception("There is not database configuration")

engine = create_engine(DATABASE_URI, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


async def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
