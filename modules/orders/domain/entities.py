from dataclasses import dataclass
from typing import List
from modules.products.domain.entities import Product
import uuid
from datetime import datetime

@dataclass(frozen=True)
class OrderV1:
    order_id: uuid.uuid4()
    customer_id: uuid.uuid4()
    order_items: list
    order_version: int = 1

    def upscale(self):

        order_total = 0
        for item in self.order_items:
            order_total += item["price"] * item["quantity"]

        return OrderV2(
            order_id=self.order_id,
            customer_id=self.customer_id,
            order_date=datetime.now().isoformat(),
            order_status="Created",
            order_items=self.order_items,
            order_total=order_total,
            order_version=2
        )

@dataclass(frozen=True)
class OrderV2:
    order_id: uuid.uuid4()
    customer_id: uuid.uuid4()
    order_date: str
    order_status: str
    order_items: List[Product]
    order_total: float
    order_version: int = 2

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date,
            "order_status": self.order_status,
            "order_items": str([str(Product(**item).to_dict())for item in self.order_items]),
            "order_total": self.order_total,
            "order_version": self.order_version
        }