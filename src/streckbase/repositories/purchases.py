from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlmodel import Session

from streckbase.models import Purchase

CODES_SUBQUERY = """
  (
    SELECT group_concat(Barcodes.code) AS codes
    FROM Barcodes
    WHERE Barcodes.item_id = p1.item_id
    GROUP BY Barcodes.item_id
  ) AS codes
"""

FEED_SELECT = """
  SELECT u.user_id, u.email, u.firstname, u.lastname, u.debt, u.lobare, u.admin,
    p1.id, p1.item_id, p1.date, p1.najs, i.name, COALESCE(p1.price, i.price) AS price,
    i.volume, i.alcohol,
  (
    SELECT group_concat(b.code) AS codes
    FROM Barcodes b
    WHERE b.item_id = p1.item_id
    GROUP BY b.item_id
  ) AS codes,
  (
    SELECT COUNT(p2.item_id)
    FROM Purchases p2
    WHERE p2.item_id = p1.item_id AND p2.user_id = u.user_id AND p2.id <= p1.id
  ) AS total
  FROM Purchases p1
  JOIN Items i ON i.item_id = p1.item_id
  JOIN Users u ON u.user_id = p1.user_id
"""


def _now_json() -> str:
    """Equivalent of JS `new Date().toJSON()` — the format v2 stores in Purchases.date."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class PurchaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_purchases(self, user_id: str, limit: int, offset: int) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(f"""
                SELECT p1.id, p1.item_id, p1.date, p1.najs,
                  COALESCE(i.name, 'Återbetalning') AS name,
                  COALESCE(p1.price, i.price, p1.amount) AS price,
                  i.volume, i.alcohol,
                  {CODES_SUBQUERY},
                (
                  SELECT COUNT(p2.item_id)
                  FROM Purchases p2
                  WHERE p2.item_id = p1.item_id AND p2.user_id = p1.user_id AND p2.id <= p1.id
                  GROUP BY p2.item_id
                ) AS total
                FROM Purchases p1
                LEFT JOIN Items i ON i.item_id = p1.item_id
                WHERE p1.user_id = :user_id
                ORDER BY p1.id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"user_id": user_id, "limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_purchase(self, purchase_id: int) -> dict[str, Any] | None:
        row = self.session.execute(
            text(f"""
                SELECT p1.id, p1.item_id, p1.date, i.name, i.price, i.volume, i.alcohol,
                  {CODES_SUBQUERY}
                FROM Purchases p1
                JOIN Items i ON i.item_id = p1.item_id
                WHERE p1.id = :id
            """),
            {"id": purchase_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_latest_user_purchase(self, user_id: str) -> dict[str, Any] | None:
        row = self.session.execute(
            text(f"""
                {FEED_SELECT}
                WHERE u.user_id = :user_id
                ORDER BY p1.id DESC
                LIMIT 1
            """),
            {"user_id": user_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_purchases(self, limit: int, offset: int) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(f"""
                SELECT p1.id, p1.item_id, p1.date, i.name, i.price, i.volume, i.alcohol,
                  {CODES_SUBQUERY}
                FROM Purchases p1
                JOIN Items i ON i.item_id = p1.item_id
                ORDER BY p1.id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_feed_purchases(self, limit: int, offset: int) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(f"""
                {FEED_SELECT}
                ORDER BY p1.id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_purchase(self, user_id: str, item_id: int, price: int, najs: bool = False) -> None:
        self.session.add(Purchase(
            user_id=user_id, item_id=item_id, date=_now_json(),
            price=price, najs=1 if najs else 0,
        ))
        self.session.commit()

    def create_repayment(self, user_id: str, amount: int) -> None:
        self.session.add(Purchase(
            user_id=user_id, item_id=None, date=_now_json(), amount=-amount,
        ))
        self.session.commit()

    def create_charge(self, user_id: str, amount: int) -> None:
        self.session.add(Purchase(
            user_id=user_id, item_id=None, date=_now_json(), price=amount,
        ))
        self.session.commit()

    def delete_purchase(self, purchase_id: int) -> None:
        self.session.execute(
            text("DELETE FROM Purchases WHERE Purchases.id = :id"),
            {"id": purchase_id},
        )
        self.session.commit()
