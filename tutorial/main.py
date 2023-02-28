from fastapi import FastAPI

import asyncio

from pydantic import BaseSettings
from typing import Any

from ..modules.orders.application.events.events import EventOrderCreated, OrderCreated
from ..modules.orders.application.commands.commands import CommandCreateOrder, CreateOrderPayload
from .consumers import subscribe_to_topic
from .dispatchers import Dispatcher

from .. import utils


class Config(BaseSettings):
    APP_VERSION: str = "1"


settings = Config()
app_configs: dict[str, Any] = {"title": "Pagos entregasalpes"}

app = FastAPI(**app_configs)
tasks = list()


@app.on_event("startup")
async def app_startup():
    global tasks
    task1 = asyncio.ensure_future(subscribe_to_topic(
        "order-event", "sub-orders", EventOrderCreated))
    task2 = asyncio.ensure_future(subscribe_to_topic(
        "command-create-order", "sub-com-order-create", CommandCreateOrder))
    tasks.append(task1)
    tasks.append(task2)


@app.on_event("shutdown")
def shutdown_event():
    global tasks
    for task in tasks:
        task.cancel()


@app.get("/prueba-reserva-pagada", include_in_schema=False)
async def prueba_reserva_pagada() -> dict[str, str]:
    payload = OrderCreated(
        id="1232321321",
        id_correlacion="389822434",
        reserva_id="6463454",
        monto=23412.12,
        monto_vat=234.0,
        fecha_creacion=utils.time_millis()
    )

    evento = EventOrderCreated(
        time=utils.time_millis(),
        ingestion=utils.time_millis(),
        datacontenttype=OrderCreated.__name__,
        reserva_pagada=payload
    )
    Dispatcher = Dispatcher()
    Dispatcher.publish_message(evento, "evento-pago")
    return {"status": "ok"}


@app.get("/prueba-pagar-reserva", include_in_schema=False)
async def prueba_pagar_reserva() -> dict[str, str]:
    payload = CreateOrderPayload(
        id_correlacion="389822434",
        reserva_id="6463454",
        monto=23412.12,
        monto_vat=234.0,
    )

    command = CommandCreateOrder(
        time=utils.time_millis(),
        ingestion=utils.time_millis(),
        datacontenttype=OrderCreated.__name__,
        data=payload
    )
    Dispatcher = Dispatcher()
    Dispatcher.publish_message(command, "command-pagar-reserva")
    return {"status": "ok"}
