from uuid import UUID
from modules.sagas.application.saga import SagasEvent
from .dtos import TransactionLogDTO

class TransactionLogRepositorySQLAlchemy:

    def __init__(self, db) -> None:
        self.db = db

    def get_by_id(self, id: UUID) -> SagasEvent:
        log_dto = self.db.session.query(TransactionLogDTO).filter_by(event_id=str(id)).one()
        return SagasEvent(**log_dto.to_dict())

    def get_order_log(self, order_id: UUID):
        log_dtos = self.db.session.query(TransactionLogDTO).filter_by(order_id=str(order_id))
        return log_dtos

    def create(self, event: SagasEvent):
        #log_dto = TransactionLogDTO(**SagasEvent.to_dict())
        log_dto = TransactionLogDTO(event_id=event.event_id,
                                    event_type=event.event_type,
                                    order_id=event.order_idm,
                                    order_status=event.order_status)
        self.db.add(log_dto)
        self.db.commit()
        self.db.refresh(log_dto)
        return log_dto

    def update(self, SagasEvent: SagasEvent):
        log_dto = self.db.session.query(TransactionLogDTO).filter_by(event_id=str(SagasEvent.order_id)).one()
        log_dto = TransactionLogDTO(**SagasEvent.to_dict())
        self.db.commit()
        return log_dto

    def delete(self, id: UUID):
        log_dto = self.db.session.query(TransactionLogDTO).filter_by(event_id=str(id)).one()
        log_dto.delete()
        self.db.commit()
        return log_dto
