from pydantic import BaseModel


class ItemRead(BaseModel):
    """Matches v2's API Item shape (services/item/item.ts)."""

    id: int | None = None
    name: str | None = None
    price: int | None = None
    price_xlob: int | None = None
    price_andra: int | None = None
    price_najs: int | None = None
    volume: int | None = None
    alcohol: float | None = None
    barcodes: list[str] = []
    imageUrl: str | None = None
    exclude_from_highscore: bool = False


class ItemCreate(BaseModel):
    name: str | None = None
    price: int | None = None
    price_xlob: int | None = None
    price_andra: int | None = None
    price_najs: int | None = None
    volume: int | None = None
    alcohol: float | None = None
    barcodes: list[str]
    imageUrl: str | None = None


class ItemUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    price: int | None = None
    price_xlob: int | None = None
    price_andra: int | None = None
    price_najs: int | None = None
    volume: int | None = None
    alcohol: float | None = None
    barcodes: list[str] = []
    exclude_from_highscore: bool = False
