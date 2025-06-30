from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.unit.unit_service import UnitService, get_unit_service
from app.unit.schema import Unit

from . import router


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Unit,
)
def get_unit_by_id(
    id: str,
    svc: UnitService = Depends(get_unit_service),
) -> Unit:
    unit_data = svc.repository.get_unit_by_id(unit_id=id)
    if not unit_data:
        error_message = "The Unit is not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        unit_data = Unit(**unit_data)
        return unit_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
