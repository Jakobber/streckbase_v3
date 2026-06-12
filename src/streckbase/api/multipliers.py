from fastapi import APIRouter

from streckbase.api.deps import MultipliersServiceDep
from streckbase.schemas.multipliers import Multipliers

router = APIRouter(prefix="/settings/multipliers", tags=["settings"])


@router.get("")
def get_multipliers(service: MultipliersServiceDep) -> Multipliers:
    return service.get_multipliers()


@router.put("")
def update_multipliers(multipliers: Multipliers, service: MultipliersServiceDep) -> Multipliers:
    return service.update_multipliers(multipliers)


@router.post("/apply", status_code=204)
def apply_multipliers(multipliers: Multipliers, service: MultipliersServiceDep) -> None:
    service.apply_multipliers(multipliers)
