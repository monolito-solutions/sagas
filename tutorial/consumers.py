import logging
import traceback
import pulsar
import _pulsar
import aiopulsar
import asyncio
from pulsar.schema import *
from ..utils import broker_host


async def subscribe_to_topic(topic: str, suscripcion: str, schema: Record, tipo_consumidor: _pulsar.ConsumerType = _pulsar.ConsumerType.Shared):
    try:
        async with aiopulsar.connect(f'pulsar://{broker_host()}:6650') as client:
            async with client.subscribe(
                topic,
                consumer_type=tipo_consumidor,
                subscription_name=suscripcion,
                schema=AvroSchema(schema)
            ) as consumidor:
                while True:
                    mensaje = await consumidor.receive()
                    print(mensaje)
                    datos = mensaje.value()
                    print(f'Event recibido: {datos}')
                    await consumidor.acknowledge(mensaje)

    except:
        logging.error(
            f'ERROR: Suscribiendose al tópico! {topic}, {suscripcion}, {schema}')
        traceback.print_exc()
