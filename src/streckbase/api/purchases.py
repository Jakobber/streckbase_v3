from fastapi import APIRouter, HTTPException

from streckbase.api.deps import PurchaseServiceDep
from streckbase.schemas.purchase import PurchaseRead

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("")
def get_purchases(service: PurchaseServiceDep, limit: int = 20, offset: int = 0) -> list[PurchaseRead]:
    return service.get_purchases(limit, offset)


@router.get("/{purchase_id}")
def get_purchase(purchase_id: int, service: PurchaseServiceDep) -> PurchaseRead:
    purchase = service.get_purchase(purchase_id)
    if purchase is None:
        raise HTTPException(status_code=404)
    return purchase
