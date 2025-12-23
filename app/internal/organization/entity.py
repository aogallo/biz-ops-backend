from pydantic import BaseModel
from sqlmodel import Field


class Organization(BaseModel):
    name: str
    slug: str = Field(unique=True, nullable=False)
