from pulsar.schema import *

class QueryMessage(Record):
    order_id = String()
    type = String(default="message")
    payload = String()