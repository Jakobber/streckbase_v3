"""Row → DTO mapping, the equivalent of v2's Mapper/forMember plumbing."""

from typing import Any

from streckbase.schemas.item import ItemRead
from streckbase.schemas.purchase import PurchaseRead
from streckbase.schemas.user import UserRead


def split_codes(codes: str | None) -> list[str]:
    return codes.split(",") if codes else []


def map_user(row: dict[str, Any] | None) -> UserRead | None:
    if row is None:
        return None
    return UserRead(
        id=row.get("user_id"),
        email=row.get("email"),
        firstname=row.get("firstname"),
        lastname=row.get("lastname"),
        debt=row.get("debt"),
        lobare=int(row.get("lobare") or 0),
        admin=bool(row.get("admin")),
        totalDebt=row.get("totalDebt"),
    )


def map_item(row: dict[str, Any] | None) -> ItemRead | None:
    if row is None:
        return None
    return ItemRead(
        id=row.get("item_id"),
        name=row.get("name"),
        price=row.get("price"),
        price_xlob=row.get("price_xlob"),
        price_andra=row.get("price_andra"),
        price_najs=row.get("price_najs"),
        volume=row.get("volume"),
        alcohol=row.get("alcohol"),
        barcodes=split_codes(row.get("codes")),
        imageUrl=row.get("image"),
        exclude_from_highscore=bool(row.get("exclude_from_highscore")),
    )


def map_purchase(row: dict[str, Any] | None) -> PurchaseRead | None:
    if row is None:
        return None
    return PurchaseRead(
        id=row.get("id"),
        date=row.get("date"),
        totalCount=row.get("total"),
        najs=bool(row.get("najs")),
        item=ItemRead(
            id=row.get("item_id"),
            name=row.get("name"),
            price=row.get("price"),
            volume=row.get("volume"),
            alcohol=row.get("alcohol"),
            barcodes=split_codes(row.get("codes")),
        ),
    )
