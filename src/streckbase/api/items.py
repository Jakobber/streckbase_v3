from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from streckbase.api.deps import ItemServiceDep
from streckbase.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/barcodes/{barcode}")
def get_barcode_item(barcode: str, service: ItemServiceDep) -> ItemRead:
    item = service.get_barcode_item(barcode)
    if item is None:
        raise HTTPException(status_code=404)
    return item


@router.get("/popular")
def get_popular_items(service: ItemServiceDep, limit: int = 20) -> list[ItemRead]:
    return service.get_popular_items(limit)


@router.get("/archived")
def get_archived_items(service: ItemServiceDep, limit: int = 20, offset: int = 0) -> list[ItemRead]:
    return service.get_archived_items(limit, offset)


@router.get("")
def get_items(service: ItemServiceDep, limit: int = 20, offset: int = 0) -> list[ItemRead]:
    return service.get_items(limit, offset)


@router.post("", status_code=201)
def create_item(item: ItemCreate, service: ItemServiceDep) -> ItemRead:
    if not item.barcodes:
        raise HTTPException(status_code=400)
    try:
        return service.create_item(item)
    except IntegrityError:
        raise HTTPException(status_code=409)


@router.get("/{item_id}")
def get_item(item_id: int, service: ItemServiceDep) -> ItemRead:
    item = service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404)
    return item


@router.put("/{item_id}")
def update_item(item_id: int, item: ItemUpdate, service: ItemServiceDep) -> ItemRead:
    item.id = item.id or item_id
    updated = service.update_item(item)
    if updated is None:
        raise HTTPException(status_code=404)
    return updated


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, service: ItemServiceDep) -> None:
    service.delete_item(item_id)


@router.put("/{item_id}/restore", status_code=204)
def restore_item(item_id: int, service: ItemServiceDep) -> None:
    service.restore_item(item_id)
