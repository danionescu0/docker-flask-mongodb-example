import pytest
from utils import MongoDb
from pymongo import MongoClient


@pytest.fixture()
def demo_db() -> MongoClient:
    db = MongoDb(host="localhost")
    db.create_connection()
    return db.connection
