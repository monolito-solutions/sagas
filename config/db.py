from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USERNAME = "root"
DB_PASSWORD = "adminadmin"
DB_HOSTNAME = "172.17.0.1"

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}/logs'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    return db

def get_base_metadata():
    return Base.metadata

def initialize_base():
    from modules.sagas.infrastructure.dtos import TransactionLogDTO
    return Base