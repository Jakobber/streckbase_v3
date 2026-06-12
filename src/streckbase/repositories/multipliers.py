from sqlalchemy import text
from sqlmodel import Session

from streckbase.schemas.multipliers import Multipliers


class MultipliersRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_multipliers(self) -> Multipliers:
        rows = self.session.execute(text("SELECT name, value FROM multipliers")).mappings().all()
        result = Multipliers()
        for row in rows:
            if row["name"] in ("xlob", "andra", "najs"):
                setattr(result, row["name"], float(row["value"]))
        return result

    def update_multipliers(self, multipliers: Multipliers) -> None:
        for name in ("xlob", "andra", "najs"):
            self.session.execute(
                text("UPDATE multipliers SET value = :value WHERE name = :name"),
                {"value": getattr(multipliers, name), "name": name},
            )
        self.session.commit()

    def apply_multipliers(self, multipliers: Multipliers) -> None:
        self.session.execute(
            text("""
                UPDATE Items SET
                  price_xlob = ROUND(price * :xlob),
                  price_andra = ROUND(price * :andra),
                  price_najs = ROUND(price * :najs)
                WHERE enabled = 1
            """),
            {"xlob": multipliers.xlob, "andra": multipliers.andra, "najs": multipliers.najs},
        )
        self.session.commit()
