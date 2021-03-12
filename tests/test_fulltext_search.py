import pytest
from pytest import FixtureRequest
import requests
import datetime
from typing import Generator
from bson.objectid import ObjectId
from utils import MongoDb

fulltext_search_host = "http://localhost:82"

expression_one = "ana has many more apples"
expression_two = "john has many more apples"


@pytest.fixture
def collection(request: FixtureRequest) -> Generator[MongoDb, None, None]:
    con = MongoDb(host="localhost")
    con.create_connection()
    con.set_collection("fulltext_search")
    param = getattr(request, "param", None)
    yield con
    for key in param:
        con.delete_many("app_text", key)


@pytest.mark.parametrize("collection", [expression_one], indirect=True)
def test_add_expression(collection):
    requests.put(
        url="{0}/fulltext".format(fulltext_search_host),
        data={"expression": expression_one},
    )
    response = collection.get({"app_text": expression_one})
    assert response[0]["app_text"] == expression_one


@pytest.mark.parametrize("collection", [expression_one, expression_two], indirect=True)
def test_search(collection):
    collection.upsert(
        ObjectId(b"foo-bar-quux"),
        {"app_text": expression_one, "indexed_date": datetime.datetime.utcnow()},
    )
    collection.upsert(
        ObjectId(b"foo-bar-baaz"),
        {"app_text": expression_two, "indexed_date": datetime.datetime.utcnow()},
    )
    response = requests.get(
        url="{0}/search/apples".format(fulltext_search_host),
    ).json()

    assert response[0]["text"].find("apples") > -1
    assert response[1]["text"].find("apples") > -1
