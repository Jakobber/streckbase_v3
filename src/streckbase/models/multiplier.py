from sqlmodel import Field, SQLModel


class Multiplier(SQLModel, table=True):
    __tablename__ = "multipliers"

    name: str = Field(primary_key=True, max_length=20)
    value: float = 1.0
