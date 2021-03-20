import pytest
import requests
from typing import Generator

from utils import Collection


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
def baesian(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "baesian")
    yield collection
    collection.drop()


def test_upsert_item(baesian):
    requests.post(url="{0}/item/{1}".format(baesian_host, item_id), data={"name": name})
    response = baesian.get({})
    assert response[0]["name"] == name
    assert response[0]["nr_votes"] == 0


def test_add_vote(baesian):
    requests.post(url="{0}/item/{1}".format(baesian_host, item_id), data={"name": name})
    requests.put(
        url="{0}/item/vote/{1}".format(baesian_host, item_id),
        data={"userid": userid_eight, "mark": 9},
    )
    requests.put(
        url="{0}/item/vote/{1}".format(baesian_host, item_id),
        data={"userid": userid_seven, "mark": 9},
    )

    response = baesian.get({})
    assert len(response[0]["marks"]) == response[0]["nr_votes"]
    assert response[0]["name"] == name
    assert response[0]["sum_votes"] == 18


def test_get_item(baesian):
    baesian.upsert(key=item_id, data=upsert_data)

    response = requests.get(
        url="{0}/item/{1}".format(baesian_host, item_id),
    ).json()
    assert response["baesian_average"] == 9.0
    assert response["sum_votes"] == 18


def test_get_items(baesian):
    baesian.upsert(key=item_id, data=upsert_data)
    response = requests.get(
        url="{0}/items".format(baesian_host),
    ).json()

    assert response[0]["name"] == name
    assert len(response[0]["marks"]) > 0


def delete_item(baesian):
    baesian.upsert(key=item_id, data=upsert_data)
    response = requests.delete(
        url="{0}/item/{1}".format(baesian_host, item_id),
    ).json()

    assert response.status_code == 200

    db_response = baesian.get({})
    assert db_response == []
