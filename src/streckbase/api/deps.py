from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from streckbase.core.db import get_session
from streckbase.services.items import ItemService
from streckbase.services.multipliers import MultipliersService
from streckbase.services.purchases import PurchaseService
from streckbase.services.users import UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


def get_item_service(session: SessionDep) -> ItemService:
    return ItemService(session)


def get_purchase_service(session: SessionDep) -> PurchaseService:
    return PurchaseService(session)


def get_multipliers_service(session: SessionDep) -> MultipliersService:
    return MultipliersService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
PurchaseServiceDep = Annotated[PurchaseService, Depends(get_purchase_service)]
MultipliersServiceDep = Annotated[MultipliersService, Depends(get_multipliers_service)]
