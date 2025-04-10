from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_number: str = Field(unique=True)
    name: str
    type: str
    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = Field(default=None, index=True)
    udpated_at: Optional[datetime] = Field(default=None)
