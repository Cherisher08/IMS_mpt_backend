from fastapi.params import Depends

from app.config import database
from app.order.order_service import OrderService, get_order_service
from app.order.utils import generate_invoice_id

from . import router


@router.get("/invoice/latest-id")
def get_latest_invoice_id(
    svc: OrderService = Depends(get_order_service),
) -> dict:
    """Get the next invoice ID that would be generated."""
    invoice_id = generate_invoice_id(db=svc.repository.database)
    return {"invoice_id": invoice_id}
