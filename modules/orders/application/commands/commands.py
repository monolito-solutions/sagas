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
