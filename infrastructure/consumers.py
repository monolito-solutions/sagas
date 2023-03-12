import logging
import traceback
import pulsar
import _pulsar
import aiopulsar
import asyncio
from pulsar.schema import *
from utils import broker_host
from modules.sagas.application.logic import get_order_logs
from modules.sagas.application.choreography import ChoreographySagaManager

manager = ChoreographySagaManager()

async def subscribe_to_topic(topic: str, subscription: str, schema: Record, consumer_type: _pulsar.ConsumerType = _pulsar.ConsumerType.Shared):
    try:
        async with aiopulsar.connect(f'pulsar://{broker_host()}:6650') as client:
            async with client.subscribe(
                topic,
                consumer_type=consumer_type,
                subscription_name=subscription,
                schema=AvroSchema(schema)
            ) as consumer:
                while True:
                    mensaje = await consumer.receive()
                    datos = mensaje.value()
                    print(f'\nEvent recibido: {datos.type}')
                    if datos.type == "GetOrderLogs":
                        get_order_logs(datos.order_id)
                    elif datos.type == "EventOrderCreated":
                        manager.start_transaction(datos.data_payload, datos.type, datos.id)
                    else:
                        try:
                            manager.handle_event(datos.data_payload, datos.type, datos.id)
                        except AttributeError:
                            print(json.loads(datos.payload))
                    await consumer.acknowledge(mensaje)

    except:
        logging.error(
            f'ERROR: While subscribing to topic! {topic}, {subscription}, {schema}')
        traceback.print_exc()