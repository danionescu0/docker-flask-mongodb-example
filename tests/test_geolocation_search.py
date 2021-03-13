import pytest
from pytest import FixtureRequest
import requests
import datetime
from typing import Generator
from bson.objectid import ObjectId
from utils import MongoDb

geolocation_host = "http://localhost:83"
NewYork = {"name": "NewYork", "lat": 40.730610, "lng": -73.935242}
JerseyCity = {"name": "JerseyCity", "lat": 40.719074, "lng": -74.050552}


@pytest.fixture
def collection(request: FixtureRequest) -> Generator[MongoDb, None, None]:
    con = MongoDb(host="localhost")
    con.create_connection()
    con.set_collection("places")
    param = getattr(request, "param", None)
    yield con
    if param:
        for key in param:
            con.delete_many("name", param["name"])


@pytest.mark.parametrize("collection", [NewYork], indirect=True)
def test_new_location(collection):
    requests.post("{0}/location".format(geolocation_host), data=NewYork)
    response = collection.get({})
    assert response[0]["name"] == NewYork["name"]

    coordinates = response[0]["location"]["coordinates"]
    assert coordinates == [NewYork["lng"], NewYork["lat"]]


@pytest.mark.parametrize("collection", [NewYork, JerseyCity], indirect=True)
def test_get_near(collection):
    collection.upsert(
        ObjectId(b"foo-bar-baaz"),
        {
            "name": NewYork["name"],
            "location": {
                "type": "Point",
                "coordinates": [NewYork["lng"], NewYork["lat"]],
            },
        },
    )
    collection.upsert(
        ObjectId(b"foo-bar-quux"),
        {
            "name": JerseyCity["name"],
            "location": {
                "type": "Point",
                "coordinates": [JerseyCity["lng"], JerseyCity["lat"]],
            },
        },
    )
    response = requests.get(
        url="{0}/location/{1}/{2}".format(
            geolocation_host, NewYork["lat"], NewYork["lng"]
        ),
        data={"max_distance": 50000},
    ).json()

    assert response[0]["name"] == NewYork["name"]
    assert response[1]["name"] == JerseyCity["name"]
