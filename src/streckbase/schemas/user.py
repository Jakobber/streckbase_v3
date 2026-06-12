from pydantic import BaseModel

from streckbase.schemas.purchase import PurchaseRead


class UserRead(BaseModel):
    """Matches v2's API User shape (services/user/user.ts)."""

    id: str | None = None
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    debt: int | None = None
    lobare: int | None = None
    admin: bool | None = None
    totalDebt: int | None = None
    # v2 omitted this key when unset; here it serializes as null, which the
    # frontend treats the same way
    purchases: list[PurchaseRead] | None = None


class UserCreate(BaseModel):
    id: str
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    lobare: int | None = 0
    admin: bool | None = False


class UserUpdate(BaseModel):
    id: str | None = None
    email: str | None = None
    debt: int | None = None
    lobare: int | None = None
    admin: bool | None = None


class RepaymentCreate(BaseModel):
    amount: int
