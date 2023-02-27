from dataclasses import dataclass
from typing import List
from modules.products.domain.entities import Product
import uuid

@dataclass(frozen=True)
class OrderV1:
    order_id: uuid.uuid4()
    customer_id: uuid.uuid4()
    order_items: list
    order_version: int = 1

@dataclass(frozen=True)
class OrderV2:
    order_id: uuid.uuid4()
    customer_id: uuid.uuid4()
    order_date: str
    order_status: str
    order_items: List[Product]
    order_total: float
    order_version: int = 2