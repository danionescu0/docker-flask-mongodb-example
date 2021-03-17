import pytest
import requests
from typing import Generator
from pytest import FixtureRequest
from bson.objectid import ObjectId

from utils import MongoDb


geolocation_host = "http://localhost:83"
new_york = {"name": "NewYork", "lat": 40.730610, "lng": -73.935242}
jersey_city = {"name": "JerseyCity", "lat": 40.719074, "lng": -74.050552}


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


@pytest.mark.parametrize("collection", [new_york], indirect=True)
def test_new_location(collection):
    requests.post("{0}/location".format(geolocation_host), data=new_york)
    response = collection.get({})
    assert response[0]["name"] == new_york["name"]

    coordinates = response[0]["location"]["coordinates"]
    assert coordinates == [new_york["lng"], new_york["lat"]]


@pytest.mark.parametrize("collection", [new_york, jersey_city], indirect=True)
def test_get_near(collection):
    collection.upsert(
        ObjectId(b"foo-bar-baaz"),
        {
            "name": new_york["name"],
            "location": {
                "type": "Point",
                "coordinates": [new_york["lng"], new_york["lat"]],
            },
        },
    )
    collection.upsert(
        ObjectId(b"foo-bar-quux"),
        {
            "name": jersey_city["name"],
            "location": {
                "type": "Point",
                "coordinates": [jersey_city["lng"], jersey_city["lat"]],
            },
        },
    )
    response = requests.get(
        url="{0}/location/{1}/{2}".format(
            geolocation_host, new_york["lat"], new_york["lng"]
        ),
        data={"max_distance": 50000},
    ).json()

    assert response[0]["name"] == new_york["name"]
    assert response[1]["name"] == jersey_city["name"]
