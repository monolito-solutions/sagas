from uuid import UUID
from modules.sagas.domain.entities import SagasEvent
from .dtos import TransactionLogDTO

class TransactionLogRepositorySQLAlchemy:

    def __init__(self, db) -> None:
        self.db = db

    def get_by_id(self, id: UUID) -> SagasEvent:
        log_dto = self.db.query(TransactionLogDTO).filter_by(event_id=str(id)).one()
        return SagasEvent(**log_dto.to_dict())

    def get_order_log(self, order_id: UUID):
        log_dtos = self.db.query(TransactionLogDTO).filter_by(order_id=str(order_id))
        return [SagasEvent(**log.to_dict()) for log in log_dtos]

    def create(self, event: SagasEvent):
        log_dto = TransactionLogDTO(**event.to_dict())
        self.db.add(log_dto)
        self.db.commit()
        self.db.refresh(log_dto)
        return log_dto

    def update(self, event: SagasEvent):
        log_dto = self.db.query(TransactionLogDTO).filter_by(event_id=str(event.order_id)).one()
        log_dto = TransactionLogDTO(**event.to_dict())
        self.db.commit()
        return log_dto

    def delete(self, id: UUID):
        log_dto = self.db.query(TransactionLogDTO).filter_by(event_id=str(id)).one()
        log_dto.delete()
        self.db.commit()
        return log_dto
