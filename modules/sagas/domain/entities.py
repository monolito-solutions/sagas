from dataclasses import dataclass

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