from typing import Any

from sqlalchemy import text
from sqlmodel import Session

from streckbase.models import Barcode, Image, Item

ITEM_SELECT = """
  SELECT Items.item_id, name, price, price_xlob, price_andra, price_najs, volume, alcohol,
    group_concat(code) AS codes, systembolaget_id, Images.thumbnail, Images.large AS image,
    exclude_from_highscore
  FROM Items
  LEFT JOIN Barcodes ON Barcodes.item_id = Items.item_id
  LEFT JOIN Images ON Images.item_id = Items.item_id
"""


class ItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_item(self, item_id: int | None) -> dict[str, Any] | None:
        if item_id is None:
            return None
        row = self.session.execute(
            text(f"""
                {ITEM_SELECT}
                WHERE Items.item_id = :id
                GROUP BY Items.item_id
                ORDER BY Items.item_id
            """),
            {"id": item_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_items(self, limit: int, offset: int, enabled: int = 1) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(f"""
                {ITEM_SELECT}
                WHERE Items.enabled = :enabled
                GROUP BY Items.item_id
                ORDER BY Items.item_id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"enabled": enabled, "limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_popular_items(self, limit: int) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text("""
                SELECT i.item_id, i.name, i.price, i.volume, i.alcohol, i.systembolaget_id,
                  img.thumbnail, img.large AS image,
                (
                  SELECT group_concat(b.code) FROM Barcodes b WHERE b.item_id = i.item_id
                ) AS codes
                FROM Purchases p
                JOIN Items i ON i.item_id = p.item_id
                LEFT JOIN Images img ON img.item_id = i.item_id
                WHERE p.date >= DATE(NOW()) - INTERVAL 1 MONTH
                GROUP BY p.item_id
                ORDER BY COUNT(p.item_id) DESC
                LIMIT :limit
            """),
            {"limit": limit},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_barcode_item_id(self, barcode: str) -> int | None:
        row = self.session.execute(
            text("""
                SELECT b.item_id AS id FROM Barcodes b
                JOIN Items i ON i.item_id = b.item_id
                WHERE b.code LIKE :code AND i.enabled = 1
            """),
            {"code": f"%{barcode}%"},
        ).mappings().first()
        return row["id"] if row else None

    def get_latest_id(self) -> int | None:
        return self.session.execute(text("SELECT MAX(item_id) AS id FROM Items")).scalar()

    def create_item(self, name: str | None, price: int | None, price_xlob: int | None,
                    price_andra: int | None, price_najs: int | None, volume: int | None,
                    alcohol: float | None, barcodes: list[str], image_url: str | None) -> int:
        # Single transaction across Items + Barcodes + Images, like v2.
        # v2 stores all barcodes comma-joined in ONE Barcodes row — kept as-is.
        item = Item(
            name=name, price=price, price_xlob=price_xlob, price_andra=price_andra,
            price_najs=price_najs, volume=volume, alcohol=alcohol,
        )
        self.session.add(item)
        self.session.flush()
        codes = ",".join(code.strip() for code in barcodes)
        self.session.add(Barcode(code=codes, item_id=item.item_id))
        if image_url:
            self.session.add(Image(item_id=item.item_id, large=image_url))
        self.session.commit()
        return item.item_id

    def update_item(self, item_id: int, name: str | None, price: int | None,
                    price_xlob: int | None, price_andra: int | None, price_najs: int | None,
                    volume: int | None, alcohol: float | None,
                    exclude_from_highscore: bool, barcodes: list[str]) -> None:
        self.session.execute(
            text("""
                UPDATE Items i, Barcodes b
                SET i.name = :name, i.price = :price, i.price_xlob = :price_xlob,
                    i.price_andra = :price_andra, i.price_najs = :price_najs,
                    i.volume = :volume, i.alcohol = :alcohol,
                    i.exclude_from_highscore = :exclude, b.code = :codes
                WHERE i.item_id = b.item_id AND i.item_id = :id
            """),
            {
                "name": name, "price": price, "price_xlob": price_xlob,
                "price_andra": price_andra, "price_najs": price_najs,
                "volume": volume, "alcohol": alcohol,
                "exclude": 1 if exclude_from_highscore else 0,
                "codes": ",".join(barcodes), "id": item_id,
            },
        )
        self.session.commit()

    def set_enabled(self, item_id: int, enabled: int) -> None:
        self.session.execute(
            text("UPDATE Items SET enabled = :enabled WHERE item_id = :id"),
            {"enabled": enabled, "id": item_id},
        )
        self.session.commit()
