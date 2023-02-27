from fastapi import APIRouter
from downscaler.orders.versioning import detect_order_version
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", status_code=202)
def create_order(order:dict):
    order = detect_order_version(order)
    print(order)
    return {"message": "Order created successfully"}