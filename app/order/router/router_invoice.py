from fastapi import APIRouter

from app.config import database
from app.order.utils import generate_invoice_id

router = APIRouter(prefix="/invoice", tags=["invoice"])


@router.get("/latest-id")
def get_latest_invoice_id():
    """Get the next invoice ID that would be generated."""
    invoice_id = generate_invoice_id(database.db)
    return {"invoice_id": invoice_id}
