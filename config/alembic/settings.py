from modules.orders.infrastructure.dtos import OrderDTO
from config.db import Base

def get_base_metadata():
    return Base.metadata

def initialize_base():
    return Base