from typing import List, Optional
from fastapi import Depends, HTTPException, status, Query
from pydantic_core import ValidationError

from app.petty_cash.petty_cash_service import PettyCashService, get_petty_cash_service
from app.petty_cash.schema import PettyCashResponse
from app.order.filters import FilterBuilder, SortBuilder

from . import router


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[PettyCashResponse],
)
def get_petty_cash_entries(
    filter: Optional[List[str]] = Query(None, description="Filters as 'field:operator:value' or 'field:value'"),
    sort: Optional[List[str]] = Query(["created_date:desc"], description="Sort fields as 'field:asc' or 'field:desc'"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(1000, ge=0, le=1000, description="Number of documents to return (0 means all)"),
    svc: PettyCashService = Depends(get_petty_cash_service),
) -> List[PettyCashResponse]:
    # Build filters from query parameters
    filters = FilterBuilder.build_filters(filter) if filter else {}
    
    # Build sort specification from query parameters
    sort_spec = SortBuilder.build_sort(sort) if sort else None
    
    # Get paginated data
    petty_cash_data = svc.repository.get_petty_cash_entries(filters=filters, sort_spec=sort_spec, skip=skip, limit=limit)
    if not petty_cash_data:
        error_message = "No Petty Cash entries found. Please create new petty cash entry"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        petty_cash_data = [PettyCashResponse(**entry) for entry in petty_cash_data]
        return petty_cash_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error. Please Contact Admin or Developer. ${e}",
        )
