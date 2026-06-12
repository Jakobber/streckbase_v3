from fastapi import APIRouter

from streckbase.api.deps import UserServiceDep
from streckbase.schemas.user import UserRead

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/highscore")
def get_monthly_highscore(service: UserServiceDep) -> list[UserRead]:
    return service.get_monthly_highscore()
