from app.config import database
from app.petty_cash.petty_cash_repository import PettyCashRepository


class PettyCashService:
    def __init__(
        self,
        petty_cash_repository: PettyCashRepository,
    ):
        self.repository = petty_cash_repository

    def delete_petty_cash(self, petty_cash_id: str):
        return self.repository.delete_petty_cash_by_id(petty_cash_id)


def get_petty_cash_service():
    petty_cash_repository = PettyCashRepository(database=database)
    svc = PettyCashService(
        petty_cash_repository=petty_cash_repository,
    )
    return svc
