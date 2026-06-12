from typing import Any

from sqlalchemy import text
from sqlmodel import Session

from streckbase.models import User

TOTAL_DEBT_SUBQUERY = """
  IFNULL(
    (SELECT SUM(i.price)
    FROM Purchases p
    JOIN Items i ON p.item_id = i.item_id
    WHERE u.user_id = p.user_id
    GROUP BY p.user_id),
  0) AS totalDebt
"""


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        row = self.session.execute(
            text(f"""
                SELECT u.user_id, u.email, u.firstname, u.lastname, u.lobare, u.admin, u.debt,
                  {TOTAL_DEBT_SUBQUERY}
                FROM Users u
                WHERE user_id = :id
            """),
            {"id": user_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_users(self, limit: int, offset: int, enabled: int = 1) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(f"""
                SELECT u.user_id, u.email, u.firstname, u.lastname, u.lobare, u.admin, u.debt,
                  {TOTAL_DEBT_SUBQUERY}
                FROM Users u
                WHERE u.enabled = :enabled
                ORDER BY u.created_at ASC
                LIMIT :limit OFFSET :offset
            """),
            {"enabled": enabled, "limit": limit, "offset": offset},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_monthly_highscore(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text("""
                SELECT u.user_id, u.email, u.firstname, u.lastname, u.lobare, u.admin,
                  IFNULL(
                    (SELECT SUM(COALESCE(p.price, i.price))
                    FROM Purchases p
                    JOIN Items i ON p.item_id = i.item_id
                    WHERE u.user_id = p.user_id
                      AND EXTRACT(YEAR FROM p.date) = YEAR(NOW())
                      AND EXTRACT(MONTH FROM p.date) = MONTH(NOW())
                      AND p.najs = 0
                      AND i.exclude_from_highscore = 0
                    GROUP BY p.user_id),
                  0) AS debt,
                  IFNULL(
                    (SELECT SUM(COALESCE(p.price, i.price))
                    FROM Purchases p
                    JOIN Items i ON p.item_id = i.item_id
                    WHERE u.user_id = p.user_id
                      AND p.najs = 0
                      AND i.exclude_from_highscore = 0
                    GROUP BY p.user_id),
                  0) AS totalDebt
                FROM Users u
                WHERE u.lobare = 1
                ORDER BY debt DESC
            """)
        ).mappings().all()
        return [dict(r) for r in rows]

    def set_enabled(self, user_id: str, enabled: int) -> None:
        self.session.execute(
            text("UPDATE Users SET enabled = :enabled WHERE user_id = :id"),
            {"enabled": enabled, "id": user_id},
        )
        self.session.commit()

    def update_debt(self, user_id: str, debt: int) -> None:
        self.session.execute(
            text("UPDATE Users SET debt = :debt WHERE user_id = :id"),
            {"debt": debt, "id": user_id},
        )
        self.session.commit()

    def create_user(self, user_id: str, firstname: str | None, lastname: str | None,
                    email: str | None, lobare: int | None, admin: bool | None) -> None:
        self.session.add(User(
            user_id=user_id,
            firstname=firstname,
            lastname=lastname,
            email=email,
            debt=0,
            lobare=lobare,
            admin=1 if admin else 0,
        ))
        self.session.commit()

    def update_user(self, user_id: str, email: str | None, debt: int | None,
                    lobare: int | None, admin: bool | None) -> None:
        self.session.execute(
            text("UPDATE Users SET email = :email, debt = :debt, lobare = :lobare, admin = :admin WHERE user_id = :id"),
            {"email": email, "debt": debt, "lobare": lobare,
             "admin": 1 if admin else 0, "id": user_id},
        )
        self.session.commit()
