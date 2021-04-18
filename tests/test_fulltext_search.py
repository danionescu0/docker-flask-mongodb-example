import pytest
from pytest import FixtureRequest
import requests
from requests.auth import HTTPBasicAuth
import datetime
from typing import Generator
from bson.objectid import ObjectId
from utils import Collection


fulltext_search_host = "http://localhost:82"

expression_one = "ana has many more apples"
expression_two = "john has many more apples"


@pytest.fixture
def fulltext_search(
    demo_db, request: FixtureRequest
) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "fulltext_search")
    yield collection
    param = getattr(request, "param", None)
    for key in param:
        collection.delete_many("app_text", key)


@pytest.mark.parametrize("fulltext_search", [expression_one], indirect=True)
def test_add_expression(fulltext_search):
    requests.put(
        url="{0}/fulltext".format(fulltext_search_host),
        data={"expression": expression_one},
        auth=HTTPBasicAuth('admin', 'changeme'),
    )
    response = fulltext_search.get({"app_text": expression_one})
    assert response[0]["app_text"] == expression_one


@pytest.mark.parametrize(
    "fulltext_search", [expression_one, expression_two], indirect=True
)
def test_search(fulltext_search):
    fulltext_search.upsert(
        ObjectId(b"foo-bar-quux"),
        {"app_text": expression_one, "indexed_date": datetime.datetime.utcnow()},
    )
    fulltext_search.upsert(
        ObjectId(b"foo-bar-baaz"),
        {"app_text": expression_two, "indexed_date": datetime.datetime.utcnow()},
    )
    response = requests.get(
        url="{0}/search/apples".format(fulltext_search_host),
        auth=HTTPBasicAuth('admin', 'changeme'),
    ).json()

    assert response[0]["text"].find("apples") > -1
    assert response[1]["text"].find("apples") > -1