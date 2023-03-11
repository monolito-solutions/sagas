import json
import time
from pulsar import Client, MessageId
from dataclasses import dataclass, field
from typing import List
import uuid


class PulsarSagas:
    def __init__(self, service_url, topic_prefix):
        self.client = Client(service_url)
        self.producers = {}
        self.consumers = {}
        self.topic_prefix = topic_prefix

    def start_step(self, step):
        topic_name = f"{self.topic_prefix}.{step.command}"
        producer = self.client.create_producer(topic_name)
        consumer = self.client.subscribe(
            topic_name, f"{step.command}-subscription")

        self.producers[step.index] = producer
        self.consumers[step.index] = consumer

    def send_command(self, step_index, command):
        producer = self.producers[step_index]
        message_id = producer.send(command.encode('utf-8'))
        return message_id

    def check_step(self, step_index, timeout_ms=1000):
        consumer = self.consumers[step_index]
        message = consumer.receive(timeout_ms)
        if message:
            event_type = message.properties()['event']
            payload = message.data().decode('utf-8')
            consumer.acknowledge(message)
            return event_type, payload
        return None

    def close(self):
        self.client.close()


@dataclass
class SagasEvent:
    event_id: str
    event_type: str
    order_id: str
    order_status: str


    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "order_id": self.order_id,
            "order_status": self.order_status
        }

@dataclass
class Step:
    index: int = 0
    command: str = ""
    event: str = ""
    error: str = ""
    compensation: str | None = None
    step_completed: bool = False
    last_event: bool = False


@dataclass
class OrderManagementTransaction:
    order_id: str
    current_event: SagasEvent
    transaction_history: List[SagasEvent]
    transaction_steps: field(default_factory=lambda: [
        Step(index=0, command="CreateOrderCommand", event="EventOrderCreated",
             error="OrderCreateError", compensation=None),
        Step(index=1, command="CheckInventoryOrder", event="InventoryChecked",
             error="EventInventoryChecked", compensation="CancelOrder"),
        Step(index=2, command="CommandDispatchOrder", event="EventOrderDispatched",
             error="ErrorDispatchingOrder", compensation="RevertInventory"),
        Step(index=3, last_event=True)
    ])

    def check_step(self, message_data):
        # Get the current step
        current_step = self.transaction_steps[self.current_event.event_type]

        # If the current step is already completed, return False
        if current_step.step_completed:
            return False

        # If the current step's event matches the received message, mark the step as completed
        if current_step.event == message_data['event']:
            current_step.step_completed = True
            return True

        # If the received message is an error event, mark the step as completed and log the error
        if message_data['event'] == current_step.error:
            current_step.step_completed = True
            self.event_to_log(message_data['event'])
            return True

        # If none of the above conditions are met, return False
        return False

    def event_to_log(self, event):
        # Append the event to the transaction history
        self.transaction_history.append(SagasEvent(
            event_id=str(uuid.uuid4()),
            event_type=event,
            order_id=self.order_id,
            order_status=self.current_event.order_status
        ))

    def execute(self, pulsar_sagas):
        # Start the first step
        pulsar_sagas.start_step(self.transaction_steps[0])

        # Send the CreateOrderCommand
        command = {
            'order_id': self.order_id,
            'order_status': self.current_event.order_status
        }
        message_id = pulsar_sagas.send_command(0, json.dumps(command))
        # Wait for the EventOrderCreated event
        while not self.check_step({'event': 'EventOrderCreated'}):
            time.sleep(0.1)

        # Send the CheckInventoryOrder command
        command = {
            'order_id': self.order_id,
            'order_status': self.current_event.order_status
        }
        message_id = pulsar_sagas.send_command(1, json.dumps(command))

        # Wait for the InventoryChecked event or EventInventoryChecked error event
        while not self.check_step({'event': 'InventoryChecked'}) and not self.check_step({'event': 'EventInventoryChecked'}):
            time.sleep(0.1)

        # If the InventoryChecked event was received, send the CommandDispatchOrder command
        if self.check_step({'event': 'InventoryChecked'}):
            command = {
                'order_id': self.order_id,
                'order_status': self.current_event.order_status
            }
            message_id = pulsar_sagas.send_command(2, json.dumps(command))

            # Wait for the EventOrderDispatched event or ErrorDispatchingOrder error event
            while not self.check_step({'event': 'EventOrderDispatched'}) and not self.check_step({'event': 'ErrorDispatchingOrder'}):
                time.sleep(0.1)

            # If the EventOrderDispatched event was received, log the event and return
            if self.check_step({'event': 'EventOrderDispatched'}):
                self.event_to_log('EventOrderDispatched')
                return

        # If the EventInventoryChecked error event was received, send the CancelOrder compensation command
        if self.check_step({'event': 'EventInventoryChecked'}):
            command = {
                'order_id': self.order_id,
                'order_status': self.current_event.order_status
            }
            message_id = pulsar_sagas.send_command(1, json.dumps(command))
            # Wait for the EventOrderCancelled event or ErrorCancellingOrder error event
            while not self.check_step({'event': 'EventOrderCancelled'}) and not self.check_step({'event': 'ErrorCancellingOrder'}):
                time.sleep(0.1)

            # If the EventOrderCancelled event was received, log the event and return
            if self.check_step({'event': 'EventOrderCancelled'}):
                self.event_to_log('EventOrderCancelled')
                return

        # If the ErrorDispatchingOrder error event was received, send the RevertInventory compensation command
        if self.check_step({'event': 'ErrorDispatchingOrder'}):
            command = {
                'order_id': self.order_id,
                'order_status': self.current_event.order_status
            }
            message_id = pulsar_sagas.send_command(2, json.dumps(command))
            # Wait for the InventoryReverted event or ErrorRevertingInventory error event
            while not self.check_step({'event': 'InventoryReverted'}) and not self.check_step({'event': 'ErrorRevertingInventory'}):
                time.sleep(0.1)

            # If the InventoryReverted event was received, log the event and return
            if self.check_step({'event': 'InventoryReverted'}):
                self.event_to_log('InventoryReverted')
                return

        # If the ErrorCancellingOrder error event was received, log the event and return
        if self.check_step({'event': 'ErrorCancellingOrder'}):
            self.event_to_log('ErrorCancellingOrder')
            return

        # If the ErrorRevertingInventory error event was received, log the event and return
        if self.check_step({'event': 'ErrorRevertingInventory'}):
            self.event_to_log('ErrorRevertingInventory')
