from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from streckbase.api.deps import UserServiceDep
from streckbase.schemas.purchase import PurchaseCreate
from streckbase.schemas.user import RepaymentCreate, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


# Registered before /{id} so the literal paths win, same as v2's route order.
@router.get("/purchases")
def get_feed_purchases(service: UserServiceDep, limit: int = 20, offset: int = 0) -> list[UserRead]:
    return service.get_feed_purchases(limit, offset)


@router.get("/archived")
def get_archived_users(service: UserServiceDep, limit: int = 1000, offset: int = 0) -> list[UserRead]:
    return service.get_archived_users(limit, offset)


@router.get("")
def get_users(service: UserServiceDep, limit: int = 20, offset: int = 0) -> list[UserRead]:
    return service.get_users(limit, offset)


@router.post("", status_code=201)
def create_user(user: UserCreate, service: UserServiceDep) -> UserRead:
    try:
        return service.create_user(user)
    except IntegrityError:
        raise HTTPException(status_code=409)


@router.put("/{user_id}/restore", status_code=204)
def restore_user(user_id: str, service: UserServiceDep) -> None:
    service.restore_user(user_id)


@router.delete("/{user_id}/disable", status_code=204)
def disable_user(user_id: str, service: UserServiceDep) -> None:
    service.disable_user(user_id)


@router.get("/{user_id}")
def get_user(user_id: str, service: UserServiceDep) -> UserRead:
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user


@router.put("/{user_id}")
def update_user(user_id: str, user: UserUpdate, service: UserServiceDep) -> UserRead:
    user.id = user.id or user_id
    updated = service.update_user(user)
    if updated is None:
        raise HTTPException(status_code=404)
    return updated


@router.get("/{user_id}/purchases")
def get_user_purchases(user_id: str, service: UserServiceDep,
                       limit: int = 20, offset: int = 0) -> UserRead:
    user = service.get_user_purchases(user_id, limit, offset)
    if user is None:
        raise HTTPException(status_code=404)
    return user


@router.get("/{user_id}/purchases/{purchase_id}")
def get_user_purchase(user_id: str, purchase_id: int, service: UserServiceDep) -> UserRead:
    user = service.get_user_purchase(user_id, purchase_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user


@router.post("/{user_id}/purchases")
def create_purchase(user_id: str, purchase: PurchaseCreate, service: UserServiceDep) -> UserRead:
    if purchase.id is None:
        raise HTTPException(status_code=400)
    user = service.create_purchase(user_id, purchase.id, purchase.najs)
    if user is None:
        raise HTTPException(status_code=404)
    return user


@router.post("/{user_id}/repayment", status_code=201)
def create_repayment(user_id: str, repayment: RepaymentCreate, service: UserServiceDep) -> dict:
    if repayment.amount <= 0:
        raise HTTPException(status_code=400)
    try:
        service.create_repayment(user_id, repayment.amount)
    except ValueError:
        raise HTTPException(status_code=500)
    return {}


@router.post("/{user_id}/charge", status_code=201)
def create_charge(user_id: str, charge: RepaymentCreate, service: UserServiceDep) -> dict:
    if charge.amount <= 0:
        raise HTTPException(status_code=400)
    try:
        service.create_charge(user_id, charge.amount)
    except ValueError:
        raise HTTPException(status_code=500)
    return {}


@router.delete("/{user_id}/purchases/{purchase_id}", status_code=202)
def delete_user_purchase(user_id: str, purchase_id: int, service: UserServiceDep) -> dict:
    try:
        service.delete_user_purchase(user_id, purchase_id)
    except ValueError:
        raise HTTPException(status_code=410)
    return {}
