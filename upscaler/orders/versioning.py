from modules.orders.domain.entities import OrderV1, OrderV2
from api.errors.exceptions import BaseAPIException
import json

def detect_order_version(order):
    """Detects the version of the order and returns the corresponding object."""
    try:
        order["order_items"] = json.loads(order["order_items"])
        return OrderV2(**order)
    except TypeError:
        try:
            return OrderV1(**order).upscale()
        except TypeError:
            raise BaseAPIException("Order version not supported")
    except KeyError:
        raise BaseAPIException("Order version not supported")