from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class Product:
    product_id: uuid.uuid4()
    supplier_id: uuid.uuid4()
    name: str
    description: str
    price: float
    quantity: int