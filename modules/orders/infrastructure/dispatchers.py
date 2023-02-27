from modules.orders.infrastructure.schema.v2.events import OrderCreatedEvent, OrderCreatedPayload
import pulsar
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
            id=str(event.id),
            customer_id=str(event.customer_id),
            order_date=str(event.order_date),
            order_status=str(event.order_status),
            order_items=event.order_items,
            order_total=float(event.order_total),
            order_version=int(event.order_version),
            creation_datetime=int(unix_time_millis(event.creation_datetime))
        )
        integration_event = OrderCreatedEvent(data=payload)
        self._publish_message(integration_event, topic, AvroSchema(OrderCreatedEvent))
