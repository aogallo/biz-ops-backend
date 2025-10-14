from sqlmodel import Field, SQLModel


class UsersRoles(SQLModel, table=True):
    role_id: int | None = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    user_auth_id: str | None = Field(
        default=None, foreign_key="user.auth_id", primary_key=True
    )
