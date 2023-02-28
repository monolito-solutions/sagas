from fastapi import APIRouter
from upscaler.orders.versioning import detect_order_version
from modules.orders.application.events.events import EventOrderCreated, OrderCreated
from infrastructure.dispatchers import Dispatcher
import utils

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", status_code=202)
def create_order(order:dict):
    order = detect_order_version(order)

    ##TODO: Create order in database

    payload = OrderCreated(**order)

    event = EventOrderCreated(
        time = utils.time_millis(),
        ingestion = utils.time_millis(),
        datacontenttype = OrderCreated.__name__,
        order_created = payload
    )

    dispatcher = Dispatcher()
    dispatcher.publish_message(event, "order-event")
    return {"message": "Order created successfully"}
