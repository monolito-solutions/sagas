import time
import os
import datetime
import requests
import json
from fastavro.schema import parse_schema
from pulsar.schema import *

epoch = datetime.datetime.utcfromtimestamp(0)
PULSAR_ENV: str = 'BROKER_HOST'


def time_millis():
    return int(time.time() * 1000)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def millis_a_datetime(millis):
    return datetime.datetime.fromtimestamp(millis/1000.0)


def broker_host():
    return os.getenv(PULSAR_ENV, default="172.17.0.1")