from sqlmodel import Session

from streckbase.repositories.multipliers import MultipliersRepository
from streckbase.schemas.multipliers import Multipliers


class MultipliersService:
    def __init__(self, session: Session):
        self.multipliers = MultipliersRepository(session)

    def get_multipliers(self) -> Multipliers:
        return self.multipliers.get_multipliers()

    def update_multipliers(self, multipliers: Multipliers) -> Multipliers:
        self.multipliers.update_multipliers(multipliers)
        return self.multipliers.get_multipliers()

    def apply_multipliers(self, multipliers: Multipliers) -> None:
        self.multipliers.apply_multipliers(multipliers)
