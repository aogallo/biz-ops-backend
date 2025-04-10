from sqlmodel import Field, SQLModel


# cuenta por pagar
class AccountPayable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
