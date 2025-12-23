from sqlmodel import SQLModel


class User(SQLModel):
    """
    Base user
    """

    auth_id: str
    permissions: list[str]
