from sqlmodel import Session

from streckbase.repositories.purchases import PurchaseRepository
from streckbase.schemas.purchase import PurchaseRead
from streckbase.services.mappers import map_purchase


class PurchaseService:
    def __init__(self, session: Session):
        self.purchases = PurchaseRepository(session)

    def get_purchase(self, purchase_id: int) -> PurchaseRead | None:
        return map_purchase(self.purchases.get_purchase(purchase_id))

    def get_purchases(self, limit: int, offset: int) -> list[PurchaseRead]:
        return [map_purchase(row) for row in self.purchases.get_purchases(limit, offset)]
