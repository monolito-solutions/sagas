from config.db import get_db
from infrastructure.repositories import TransactionLogRepositorySQLAlchemy
from infrastructure.dispatchers import Dispatcher
from modules.sagas.application.messages.payloads import QueryMessage
import traceback
import json

def get_order_logs(order_id):
    db = get_db()
    try:
        repository = TransactionLogRepositorySQLAlchemy(db)
        logs = repository.get_order_log(order_id)
        message = QueryMessage(
            order_id = order_id,
            type = "OrderLogsResponse",
            payload=json.dumps(logs))
        dispatcher = Dispatcher()
        dispatcher.publish_message(message, "order-queries")
    except Exception as e:
        traceback.print_exc(e)
    finally:
        db.close()