from fastapi import Depends
from sqlmodel import Session

from app.infrastructure.database import get_current_session


class BaseRepository:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db if db is not None else get_current_session()


def get_base_repository(db: Session = Depends(get_current_session)) -> BaseRepository:
    return BaseRepository(db=db)
