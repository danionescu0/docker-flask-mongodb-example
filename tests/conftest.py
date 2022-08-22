import pytest
from utils import MongoDb
from pymongo import MongoClient


@pytest.fixture()
def demo_db() -> MongoClient:
    db = MongoDb(host="mongodb")
    db.create_connection()
    return db.connection
