from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    __tablename__ = "Items"

    item_id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    price: int | None = None
    volume: int | None = None
    alcohol: float | None = None
    systembolaget_id: int | None = None
    enabled: int = 1
    price_xlob: int | None = None
    price_andra: int | None = None
    price_najs: int | None = None
    exclude_from_highscore: int = 0
