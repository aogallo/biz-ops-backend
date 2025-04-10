from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)
    date_birth: str
    comercial_activity: str
