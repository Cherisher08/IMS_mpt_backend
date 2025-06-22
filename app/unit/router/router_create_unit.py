from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.unit.unit_service import UnitService, get_unit_service
from app.unit.schema import Unit

from . import router


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Unit,
)
def create_unit(
    payload: Unit,
    svc: UnitService = Depends(get_unit_service),
) -> Unit:
    unit_data = svc.repository.create_unit(unit=payload)
    if not unit_data:
        error_message = "The Unit is not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        unit_data = Unit(**unit_data)
        return unit_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
