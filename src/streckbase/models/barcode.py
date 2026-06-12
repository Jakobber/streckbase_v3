from sqlmodel import Field, SQLModel


class Barcode(SQLModel, table=True):
    __tablename__ = "Barcodes"

    code: str = Field(primary_key=True, max_length=64)
    item_id: int
