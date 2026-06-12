from sqlmodel import Session

from streckbase.repositories.items import ItemRepository
from streckbase.schemas.item import ItemCreate, ItemRead, ItemUpdate
from streckbase.services.mappers import map_item


class ItemService:
    def __init__(self, session: Session):
        self.items = ItemRepository(session)

    def get_item(self, item_id: int | None) -> ItemRead | None:
        return map_item(self.items.get_item(item_id))

    def get_items(self, limit: int, offset: int) -> list[ItemRead]:
        return [map_item(row) for row in self.items.get_items(limit, offset, enabled=1)]

    def get_archived_items(self, limit: int, offset: int) -> list[ItemRead]:
        return [map_item(row) for row in self.items.get_items(limit, offset, enabled=0)]

    def get_popular_items(self, limit: int) -> list[ItemRead]:
        return [map_item(row) for row in self.items.get_popular_items(limit)]

    def get_barcode_item(self, barcode: str) -> ItemRead | None:
        return self.get_item(self.items.get_barcode_item_id(barcode))

    def create_item(self, item: ItemCreate) -> ItemRead | None:
        self.items.create_item(
            item.name, item.price, item.price_xlob, item.price_andra, item.price_najs,
            item.volume, item.alcohol, item.barcodes, item.imageUrl,
        )
        return self.get_item(self.items.get_latest_id())

    def update_item(self, item: ItemUpdate) -> ItemRead | None:
        self.items.update_item(
            item.id, item.name, item.price, item.price_xlob, item.price_andra,
            item.price_najs, item.volume, item.alcohol,
            item.exclude_from_highscore, item.barcodes,
        )
        return self.get_item(item.id)

    def delete_item(self, item_id: int) -> None:
        self.items.set_enabled(item_id, 0)

    def restore_item(self, item_id: int) -> None:
        self.items.set_enabled(item_id, 1)
