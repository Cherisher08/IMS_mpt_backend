from fastapi.params import Depends, Query

from app.config import database
from app.order.order_service import OrderService, get_order_service
from app.order.utils import generate_invoice_id, generate_order_id
from app.auth.schema import Branch
from app.order.schema import BillingMode

from . import router


@router.get("/invoice/latest-id")
def get_latest_invoice_id(
    branch: Branch = Query(default=Branch.PADUR, description="Branch code"),
    billing_mode: BillingMode = Query(
        default=BillingMode.B2B, description="Billing mode (B2B or B2C)"
    ),
    svc: OrderService = Depends(get_order_service),
) -> dict:
    """Get the next invoice ID that would be generated for the specified branch and billing mode."""
    invoice_id = generate_invoice_id(
        db=svc.repository.database, branch=branch, billing_mode=billing_mode
    )
    return {"invoice_id": invoice_id}


@router.get("/order/latest-id")
def get_latest_order_id(
    branch: Branch = Query(default=Branch.PADUR, description="Branch code"),
    svc: OrderService = Depends(get_order_service),
) -> dict:
    """Get the next order ID that would be generated."""
    order_id = generate_order_id(db=svc.repository.database, branch=branch)
    return {"order_id": order_id}
