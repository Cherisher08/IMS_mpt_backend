from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.unit.unit_service import UnitService, get_unit_service
from app.unit.schema import Unit


from . import router


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[Unit],
)
def get_units(
    svc: UnitService = Depends(get_unit_service),
) -> List[Unit]:
    unit_data = svc.repository.get_units()
    if not unit_data:
        error_message = (
            "No Units Found. Please create new unit"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        unit_data = [Unit(**unit) for unit in unit_data]
        return unit_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
