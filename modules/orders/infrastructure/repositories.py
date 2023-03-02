from uuid import UUID
from modules.orders.domain.entities import OrderV2
from .dtos import OrderDTO


class OrdersRepositorySQLAlchemy:

    def __init__(self, db) -> None:
        self.db = db

    def get_by_id(self, id: UUID) -> OrderV2:
        order_dto = self.db.session.query(OrderDTO).filter_by(id=str(id)).one()
        return OrderV2(**order_dto.to_dict())

    def create(self, OrderV2: OrderV2):
        order_dto = OrderDTO(**OrderV2.to_dict())
        self.db.add(order_dto)
        self.db.commit()
        self.db.refresh(order_dto)
        return order_dto

    def delete(self, id: UUID):
        # TODO
        raise NotImplementedError
