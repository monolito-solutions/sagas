from sqlalchemy import String, Column, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from config.db import Base

class OrderDTO(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    customer_id = Column(UUID(as_uuid=True), index=True)
    order_date = Column(String, index=True)
    order_status = Column(String, index=True)
    order_items = Column(String, index=True)
    order_total = Column(Float, index=True)
    order_version = Column(Integer, index=True)