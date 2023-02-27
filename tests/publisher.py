from modules.orders.infrastructure.schema.v2.events import OrderCreatedEvent, OrderCreatedPayload, ProductPayload
from modules.orders.domain.entities import OrderV2
import pulsar, _pulsar
from pulsar.schema import AvroSchema
from utils.pulsar import broker_host

import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Dispatcher:
    def _publish_message(self, message, topic, schema):
        client = pulsar.Client(f'pulsar://{broker_host()}:6650')
        publisher = client.create_producer(topic, schema=AvroSchema(OrderCreatedEvent))
        publisher.send(message)
        client.close()

    def publish_event(self, event, topic):
        payload = OrderCreatedPayload(
            order_id=str(event.order_id),
            customer_id=str(event.customer_id),
            order_date=str(event.order_date),
            order_status=str(event.order_status),
            order_items=str([str(ProductPayload(**item))for item in event.order_items]),
            order_total=float(event.order_total),
            order_version=int(event.order_version),
        )
        integration_event = OrderCreatedEvent(data=payload)
        #print(integration_event)
        self._publish_message(integration_event, topic, AvroSchema(OrderCreatedEvent))


if __name__ == "__main__":

    order = {
    "order_id": "90c6316b-aa6c-4377-bfb5-ba2d40481bc2",
    "customer_id": "fdc2db56-1eb8-4f7e-90b2-bca6d44af667",
    "order_date": "2023-02-27T08:05:08.464634",
    "order_status": "Created",
    "order_items": [
      {
        "product_id": "9cad4dc7-50c0-44d7-9ed9-3f887a9d565b",
        "supplier_id": "987eba3c-ae2b-4382-86f9-7ea238733e05",
        "name": "product1",
        "description": "Test Desc",
        "price": 33000.0,
        "quantity": 5
      }
        ],
    "order_total": 33000
    }


    event = OrderV2(**order)
    despachador = Dispatcher()
    despachador.publish_event(event, "test")