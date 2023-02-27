import pulsar, _pulsar
from utils.pulsar import broker_host
from modules.orders.infrastructure.schema.v2.events import OrderCreatedEvent
from pulsar.schema import AvroSchema
import traceback
import json
cliente = None

try:
    cliente = pulsar.Client(f'pulsar://{broker_host()}:6650')
    consumidor = cliente.subscribe('test', consumer_type=_pulsar.ConsumerType.Shared, subscription_name='test', schema=AvroSchema(OrderCreatedEvent))

    while True:
        mensaje = consumidor.receive()
        print(json.loads(mensaje.value().data.order_items))

        consumidor.acknowledge(mensaje)     

    cliente.close()
except:
    print('ERROR: Suscribiendose al tópico de eventos!')
    traceback.print_exc()
    if cliente:
        cliente.close()