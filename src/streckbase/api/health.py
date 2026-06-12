from fastapi import APIRouter
from sqlmodel import text

from streckbase.api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    session.exec(text("SELECT 1"))
    # Same status string as v2, in case anything matches on it
    return {"status": "okeeey"}
