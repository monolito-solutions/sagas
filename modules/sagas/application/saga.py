from dataclasses import dataclass, field
from typing import List

@dataclass
class SagasEvent:
    event_id:str
    event_type: str
    order_id:str
    order_status:str

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "order_id": self.order_id,
            "order_status": self.order_status
        }

@dataclass
class Step:
    index:int = 0
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
        Step(index=0, command="CreateOrderCommand", event="EventOrderCreated", error="OrderCreateError", compensation=None),
        Step(index=1, command="CheckInventoryOrder", event="InventoryChecked", error="EventInventoryChecked", compensation="CancelOrder"),
        Step(index=2, command="CommandDispatchOrder", event="EventOrderDispatched", error="ErrorDispatchingOrder", compensation="RevertInventory"),
        Step(index=3, last_event=True)
    ])

    def check_step(self, message_data):
        ##TODO: 1. Si el comando es Create Order crear el transaction history y poner como evento actual
        ##TODO: 2. De lo contrario, comparar current event con el valor recibido en el parámetro
        pass

    def event_to_log(self, event):
        pass