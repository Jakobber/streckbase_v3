from pydantic import BaseModel

from streckbase.schemas.item import ItemRead


class PurchaseRead(BaseModel):
    """Matches v2's API Purchase shape (services/purchase/purchase.ts)."""

    id: int | None = None
    date: str | None = None
    totalCount: int | None = None
    item: ItemRead | None = None
    najs: bool = False


class PurchaseCreate(BaseModel):
    """Body of POST /users/{userId}/purchases — an item plus optional najs flag."""

    id: int | None = None
    najs: bool = False
