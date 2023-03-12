from sqlalchemy import String, Column
from sqlalchemy.types import Float
from config.db import Base

class TransactionLogDTO(Base):
    __tablename__ = "transactions"

    event_id = Column(String(36), primary_key = True, index = True)
    event_type = Column(String(36))
    order_id = Column(String(36), index=True)
    order_status = Column(String(50))
    timestamp = Column(String(50))

    def to_dict(self):
        return {
            "event_id" : self.event_id,
            "event_type" : self.event_type,
            "order_id" : self.order_id,
            "order_status" : self.order_status,
            "timestamp": self.timestamp
        }