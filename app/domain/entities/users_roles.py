from typing import Optional, Dict, Any, ClassVar
from sqlmodel import Field, SQLModel


class UsersRoles(SQLModel, table=True):
    role_id: Optional[int] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    user_auth_id: Optional[str] = Field(
        default=None, foreign_key="user.auth_id", primary_key=True
    )
