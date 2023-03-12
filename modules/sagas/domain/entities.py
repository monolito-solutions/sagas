from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class SagasEvent:
    event_id: str
    event_type: str
    order_id: str
    order_status: str
    timestamp: float = None
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "order_id": self.order_id,
            "order_status": self.order_status,
            "timestamp": self.timestamp
        }

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()