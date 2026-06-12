from typing import Any

import httpx

from streckbase.schemas.systembolaget import SystembolagetItem

SEARCH_URL = "https://systembolaget.se/api/productsearch/search/sok-dryck/"


def _to_camel(obj: Any) -> Any:
    """Lower-cases the first letter of every key, like v2's toCamel helper."""
    if isinstance(obj, list):
        return [_to_camel(v) if isinstance(v, (dict, list)) else v for v in obj]
    if isinstance(obj, dict):
        return {
            (k[:1].lower() + k[1:]): _to_camel(v) if isinstance(v, (dict, list)) else v
            for k, v in obj.items()
        }
    return obj


class SystembolagetService:
    def _extract_product_data(self, data: Any, article: str) -> SystembolagetItem | None:
        if not data or not data.get("productSearchResults"):
            return None

        for product in data["productSearchResults"]:
            if article in str(product.get("productNumber", "")):
                image = product.get("productImage") or {}
                name_bold = product.get("productNameBold")
                name_thin = product.get("productNameThin")
                volume = product.get("volume")
                return SystembolagetItem(
                    name=f"{name_bold}, {name_thin}" if name_thin else name_bold,
                    producer=product.get("producerName"),
                    price=product.get("price"),
                    imageUrl=f"https:{image['imageUrl']}" if image.get("imageUrl") else None,
                    volume=volume / 10 if volume else None,  # milliliter -> centiliter
                )
        return None

    async def search_item(self, article: str) -> SystembolagetItem | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(SEARCH_URL, params={"searchquery": article})
            data = _to_camel(response.json())
            return self._extract_product_data(data, article)
