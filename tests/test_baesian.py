import pytest
import requests
import datetime
from typing import Generator

from utils import MongoDb

baesian_host = "http://localhost:84"

name = "Cicero"
item_id = 1
userid_seven = 7
userid_eight = 8

upsert_data = {
    "marks": [{"mark": 9, "userid": userid_eight}, {"mark": 9, "userid": userid_seven}],
    "name": name,
    "nr_votes": 2,
    "sum_votes": 18,
}


@pytest.fixture
def collection() -> Generator[MongoDb, None, None]:
    con = MongoDb(host="localhost")
    con.create_connection()
    con.set_collection("baesian")
    yield con
    con.drop()


def test_upsert_item(collection):
    requests.post(url="{0}/item/{1}".format(baesian_host, item_id), data={"name": name})
    response = collection.get({})
    assert response[0]["name"] == name
    assert response[0]["nr_votes"] == 0


def test_add_vote(collection):
    requests.post(url="{0}/item/{1}".format(baesian_host, item_id), data={"name": name})
    requests.put(
        url="{0}/item/vote/{1}".format(baesian_host, item_id),
        data={"userid": userid_eight, "mark": 9},
    )
    requests.put(
        url="{0}/item/vote/{1}".format(baesian_host, item_id),
        data={"userid": userid_seven, "mark": 9},
    )

    response = collection.get({})
    assert len(response[0]["marks"]) == response[0]["nr_votes"]
    assert response[0]["name"] == name
    assert response[0]["sum_votes"] == 18


def test_get_item(collection):
    collection.upsert(key=item_id, data=upsert_data)

    response = requests.get(
        url="{0}/item/{1}".format(baesian_host, item_id),
    ).json()
    assert response["baesian_average"] == 9.0
    assert response["sum_votes"] == 18


def test_get_items(collection):
    collection.upsert(key=item_id, data=upsert_data)
    response = requests.get(
        url="{0}/items".format(baesian_host),
    ).json()

    assert response[0]["name"] == name
    assert len(response[0]["marks"]) > 0


def delete_item(collection):
    collection.upsert(key=item_id, data=upsert_data)
    response = requests.delete(
        url="{0}/item/{1}".format(baesian_host, item_id),
    ).json()

    assert response.status_code == 200

    db_response = collection.get({})
    assert db_response == []
