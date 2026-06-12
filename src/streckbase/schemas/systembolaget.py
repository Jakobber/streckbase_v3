from pydantic import BaseModel


class SystembolagetItem(BaseModel):
    name: str | None = None
    producer: str | None = None
    price: float | None = None
    imageUrl: str | None = None
    volume: float | None = None
