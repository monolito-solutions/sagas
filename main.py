from fastapi import FastAPI
import uvicorn
import asyncio
import uuid
import random
import json
import utils
from sqlalchemy.exc import OperationalError
from infrastructure.consumers import subscribe_to_topic
from modules.orders.application.events.events import OrderEvent
from modules.orders.application.commands.commands import OrderCommand, CommandPayload
from config.db import Base, engine, initialize_base
from infrastructure.dispatchers import Dispatcher
from modules.sagas.application.saga import SagasEvent
from modules.sagas.infrastructure.repositories import TransactionLogRepositorySQLAlchemy
from config.db import get_db

app = FastAPI()

tasks = list()
initialize_base()
try:
    Base.metadata.create_all(bind=engine)
except OperationalError:
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def app_startup():
    global tasks
    task1 = asyncio.ensure_future(subscribe_to_topic(
        "order-events", "sub-sagas", OrderEvent))
    task2 = asyncio.ensure_future(subscribe_to_topic(
        "order-commands", "com-sagas", OrderCommand))
    tasks.append(task1)
    tasks.append(task2)


@app.on_event("shutdown")
def shutdown_event():
    global tasks
    for task in tasks:
        task.cancel()

@app.get("/orders")
def create_order_endpoint():
    event_payload = CommandPayload(
        order_id = str(uuid.uuid4()),
        customer_id = str(uuid.uuid4()),
        order_date = str("2023-02-27T08:05:08.464634"),
        order_status = "Created",
        order_items = json.dumps([{ "product_id": "9cad4dc7-50c0-44d7-9ed9-3f887a9d565b", "supplier_id": "987eba3c-ae2b-4382-86f9-7ea238733e05", "name": "product1", "description": "Test Desc", "price": 33000.0, "quantity": 5 } ]),
        order_total = float(random.randint(2, 15000)),
        order_version = int(random.randint(1,10))
    )

    event1 = OrderCommand(
        time = utils.time_millis(),
        ingestion = utils.time_millis(),
        datacontenttype = CommandPayload.__name__,
        data_payload = event_payload,
        type = "CommandCreateOrder"
    )
    event2 = OrderCommand(
        time = utils.time_millis(),
        ingestion = utils.time_millis(),
        datacontenttype = CommandPayload.__name__,
        data_payload = event_payload,
        type = "CommandCheckInventory"
    )

    event3 = OrderCommand(
        time = utils.time_millis(),
        ingestion = utils.time_millis(),
        datacontenttype = CommandPayload.__name__,
        data_payload = event_payload,
        type = "CommandDispatchOrder"
    )
    print(event1)
    print(event2)
    dispatcher = Dispatcher()
    dispatcher.publish_message(event1, "order-commands")
    dispatcher.publish_message(event2, "order-commands")
    dispatcher.publish_message(event3, "order-commands")
    return {"message": "Order created successfully"}

@app.get("/test")
def test_db_sagas():
    db = get_db()
    repository = TransactionLogRepositorySQLAlchemy(db)
    event = SagasEvent(
        event_id = uuid.uuid4(),
        event_type="TestEvent",
        order_id = uuid.uuid4(),
        order_status = random.choice(["Created", "Checking Inventory", "Ready for Dispatch"])
    )
    response = repository.create(event)
    print(response)
    db.close()
    return {"event": response}

@app.get("/get_test")
def test_get_db(order_id: uuid.UUID):
    db = get_db()
    repository = TransactionLogRepositorySQLAlchemy(db)
    response = repository.get_order_log(order_id)
    db.close()
    return {"events": response}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=1250)