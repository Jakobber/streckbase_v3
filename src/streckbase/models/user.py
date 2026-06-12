from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "Users"

    user_id: str = Field(primary_key=True, max_length=64)
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    debt: int | None = None
    lobare: int | None = 0
    admin: int | None = 0
    created_at: datetime | None = None
    enabled: int = 1
