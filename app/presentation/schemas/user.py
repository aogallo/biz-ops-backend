from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    auth_id: str
    email: str
    picture: Optional[str]
