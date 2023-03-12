import json
import time
from dataclasses import dataclass, field
from typing import List, Union
import uuid
from infrastructure.dispatchers import Dispatcher
from modules.orders.application.commands.commands import CommandPayload, OrderCommand
from modules.sagas.infrastructure.repositories import TransactionLogRepositorySQLAlchemy
from modules.sagas.domain.entities import SagasEvent
from config.db import get_base_metadata, get_db
import utils



@dataclass
class Step:
    index: int = 0
    event: str = ""
    error: str = ""
    compensation: Union[str, None] = None
    step_completed: bool = False
    last_event: bool = False

def get_transaction_steps():
    return [
        Step(index=0, event="EventOrderCreated",
                error="OrderCreateError", compensation=None),
        Step(index=1, event="EventInventoryChecked",
                error="ErrorCheckingInventory", compensation="CancelOrder"),
        Step(index=2, event="EventOrderDispatched",
                error="ErrorDispatchingOrder", compensation="RevertInventory", last_event=True)
    ]

@dataclass
class OrderManagementTransaction:
    order_id: str
    current_event: SagasEvent
    transaction_history: List[SagasEvent]
    transaction_steps: List[Step] = field(default_factory=get_transaction_steps)

    def event_to_log(self, event):
        # Append the event to the transaction history
        event = SagasEvent(
            event_id=str(event.event_id),
            event_type=event.event_type,
            order_id=event.order_id,
            order_status=event.order_status
        )
        db = get_db()
        self.transaction_history.append(event)
        repository = TransactionLogRepositorySQLAlchemy(db)
        repository.create(event)
        db.close()

class ChoreographySagaManager:

    errors = ["OrderCreateError", "ErrorCheckingInventory", "ErrorDispatchingOrder"]

    def __init__(self):
        self.transactions: Dict[str, OrderManagementTransaction] = {}

    def start_transaction(self, message_data, event_type, event_id):
        first_event = SagasEvent(event_id, event_type, message_data.order_id, message_data.order_status)
        transaction = OrderManagementTransaction(first_event.order_id, first_event, [])
        self.transactions[message_data.order_id] = transaction
        transaction.event_to_log(first_event)

    def handle_event(self, message_data, event_type, event_id):
        event = SagasEvent(event_id, event_type, message_data.order_id, message_data.order_status)
        order_id = event.order_id
        transaction = self.transactions.get(order_id)
        if transaction is None:
            return

        transaction.event_to_log(event)
        self._execute_step(transaction, event, message_data)

    def handle_error(self, compensation, message):
        if compensation is not None:
            command_payload = CommandPayload(
            order_id = message.order_id,
            customer_id = message.customer_id,
            order_date = message.order_id,
            order_status = message.order_status,
            order_items = message.order_items,
            order_total = float(message.order_total),
            order_version = int(message.order_version)
            )

            compensation_command = OrderCommand(
                time = utils.time_millis(),
                ingestion = utils.time_millis(),
                datacontenttype = CommandPayload.__name__,
                data_payload = command_payload,
                type = compensation
            )
            dispatcher = Dispatcher()
            dispatcher.publish_message(compensation_command, "order-commands")
        return

    def _execute_step(self, transaction: OrderManagementTransaction, event: SagasEvent, message):
        current_step = transaction.transaction_steps[0]
        for step in transaction.transaction_steps:
            if step.event == event.event_type or step.error == event.event_type:
                current_step = step
                break

        if event.event_type in self.errors:
            # Compensating action for the failed event
            compensation_event_type = current_step.compensation
            compensation_event = SagasEvent(str(uuid.uuid4()), compensation_event_type, event.order_id, event.order_status)
            for index in range(current_step.index, -1, -1):
                self.handle_error(transaction.transaction_steps[index].compensation, message)
            return

        current_step.step_completed = True
        if current_step.compensation is not None:
            transaction.current_event = event
        if current_step.last_event:
            self.transactions.pop(transaction.order_id)
            return