from app.config import database
from app.unit.unit_repository import UnitRepository


class UnitService:
    def __init__(self, unit_repository: UnitRepository):
        self.repository = unit_repository


def get_unit_service():
    unit_repository = UnitRepository(database=database)
    svc = UnitService(
        unit_repository=unit_repository
    )
    return svc
