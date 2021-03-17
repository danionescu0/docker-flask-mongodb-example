import pytest, requests
import datetime

from utils import MongoDb


random_host = "http://localhost:800"


@pytest.fixture
def collection():
    con = MongoDb(host="localhost")
    con.create_connection()
    con.set_collection("random_numbers")
    yield con
    con.drop()


def test_random_insert(collection):
    requests.put(
        url="{0}/random".format(random_host),
        data={"upper": 100, "lower": 10},
    ).json()

    response = collection.get(dict())
    assert len(response) == 1
    assert response[0]["_id"] == "lasts"

    items = response[0]["items"]
    assert len(items) == 1

    first_item = items[0]
    assert isinstance(first_item["date"], datetime.datetime)
    assert 10 < int(first_item["value"]) < 100


def test_random_generator():
    response = requests.get(
        url="{0}/random?lower=10&upper=100".format(random_host)
    ).json()
    assert 10 < int(response) < 100


def test_last_number_list(collection):
    collection.upsert(
        "lasts",
        {
            "items": [
                {"date": datetime.datetime(2021, 3, 1, 0, 0, 000000), "value": 10},
                {"date": datetime.datetime(2021, 3, 2, 0, 0, 000000), "value": 11},
                {"date": datetime.datetime(2021, 3, 3, 0, 0, 000000), "value": 12},
                {"date": datetime.datetime(2021, 3, 4, 0, 0, 000000), "value": 13},
                {"date": datetime.datetime(2021, 3, 5, 0, 0, 000000), "value": 14},
            ]
        },
    )
    response = requests.get(url="{0}/random-list".format(random_host)).json()
    assert response == [10, 11, 12, 13, 14]
