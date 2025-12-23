from sqlmodel import Field, SQLModel


class Module(SQLModel, table=True):
    id: int
    name: str = Field(unique=True)
    is_active: bool = Field(default=False)
