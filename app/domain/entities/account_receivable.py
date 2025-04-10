from sqlmodel import Field, SQLModel


class AccountReceivable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
