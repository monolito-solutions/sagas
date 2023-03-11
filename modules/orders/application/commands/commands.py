from pulsar.schema import *
from utils import time_millis
import uuid


class CommandPayload(Record):
    order_id = String()
    customer_id = String()
    order_date = String()
    order_status = String()
    order_items = String()
    order_total = Float()
    order_version = Long()

    @staticmethod
    def random():
        return CommandPayload(order_id = str(uuid.uuid1()),
        customer_id = str(uuid.uuid4()),
        order_date = str("2023-02-27T08:05:08.464634"),
        order_status = "Created",
        order_items = json.dumps([{ "product_id": "9cad4dc7-50c0-44d7-9ed9-3f887a9d565b", "supplier_id": "987eba3c-ae2b-4382-86f9-7ea238733e05", "name": "product1", "description": "Test Desc", "price": 33000.0, "quantity": 5 } ]),
        order_total = float(random.randint(2, 15000)),
        order_version = int(random.randint(1,10)))


class OrderCommand(Record):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String(default="v2")
    type = String(default="Command")
    datacontenttype = String()
    service_name = String(default="sagas.entregasalpes")
    data_payload = CommandPayload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}
