import uuid

from pulsar.schema import Record, Long, String

def time_millis():
    return int(time.time() * 1000)

class Mensaje(Record):
    id = String(default=str(uuid.uuid4()))
    time = Long()
    ingestion = Long(default=time_millis())
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()