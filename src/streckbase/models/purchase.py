from sqlmodel import Field, SQLModel


class Purchase(SQLModel, table=True):
    __tablename__ = "Purchases"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str | None = Field(default=None, max_length=64)
    item_id: int | None = None
    # Stored as text in the legacy schema (ISO 8601 strings via Date.toJSON())
    date: str | None = None
    amount: int | None = None
    price: int | None = None
    najs: int = 0
