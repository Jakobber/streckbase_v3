import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from streckbase.schemas.systembolaget import SystembolagetItem
from streckbase.services.systembolaget import SystembolagetService

router = APIRouter(prefix="/systembolaget", tags=["systembolaget"])

service = SystembolagetService()


@router.get("")
async def search_item(q: str | None = None) -> SystembolagetItem | None:
    if not q:
        raise HTTPException(status_code=400)
    return await service.search_item(q)


@router.get("/image")
async def get_image(url: str | None = None) -> StreamingResponse:
    if not url:
        raise HTTPException(status_code=400)

    client = httpx.AsyncClient()
    request = client.build_request("GET", url)
    response = await client.send(request, stream=True)

    async def stream():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        stream(),
        status_code=response.status_code,
        media_type=response.headers.get("content-type"),
    )
