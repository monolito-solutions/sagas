from sqlalchemy import String
from config.db import Base

class TransactionLogDTO(Base):
    __tablename__ = "transactions"

    event_id = Column(String())
    event_type = Column(String())
    order_id = Column(String())
    order_status = Column(String())