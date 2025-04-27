from fastapi import Depends
from sqlmodel import Session

from app.infrastructure.database import get_session


class BaseRepository:
    def __init__(self, db: Session = Depends(get_session)) -> None:
        self.db = db
