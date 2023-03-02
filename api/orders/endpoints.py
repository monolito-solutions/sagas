from fastapi import APIRouter, Depends
from upscaler.orders.versioning import detect_order_version
from sqlalchemy.exc import IntegrityError
from api.errors.exceptions import BaseAPIException
from modules.orders.application.events.events import EventOrderCreated, OrderCreated, ProductPayload
from modules.orders.infrastructure.repositories import OrdersRepositorySQLAlchemy
from infrastructure.dispatchers import Dispatcher
from config.db import get_db
import utils

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", status_code=202)
def create_order(order:dict, db=Depends(get_db)):
    order = detect_order_version(order)

    try:
        repository = OrdersRepositorySQLAlchemy(db)
        repository.create(order)
    except IntegrityError:
        raise BaseAPIException(f"Error creating order, primary key integrity violated (Duplicate ID)", 400)
    except Exception as e:
        raise BaseAPIException(f"Error creating order: {e}", 500)

    payload = OrderCreated(
        order_id = str(order.order_id),
        customer_id = str(order.customer_id),
        order_date = str(order.order_date),
        order_status = str(order.order_status),
        order_items = str([str(ProductPayload(**item))for item in order.order_items]),
        order_total = float(order.order_total),
        order_version = int(order.order_version)
    )

    event = EventOrderCreated(
        time = utils.time_millis(),
        ingestion = utils.time_millis(),
        datacontenttype = OrderCreated.__name__,
        order_created = payload
    )

    dispatcher = Dispatcher()
    dispatcher.publish_message(event, "order-event")
    return {"message": "Order created successfully"}
