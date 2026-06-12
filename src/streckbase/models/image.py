from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    __tablename__ = "Images"

    item_id: int = Field(primary_key=True)
    thumbnail: str | None = Field(default=None, max_length=255)
    large: str | None = Field(default=None, max_length=255)
