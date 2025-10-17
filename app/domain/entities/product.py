from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str = Field(unique=True)
