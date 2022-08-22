import pytest
import requests
from typing import Generator
from bson.objectid import ObjectId

from utils import Collection


geolocation_host = "http://localhost:83"
new_york = {"name": "NewYork", "lat": 40.730610, "lng": -73.935242}
jersey_city = {"name": "JerseyCity", "lat": 40.719074, "lng": -74.050552}
authentication_response = requests.post(
    geolocation_host + "/login",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"username": "admin", "password": "secret"},
)

assert isinstance(authentication_response.json(), dict)
assert "access_token" in authentication_response.json()
token = authentication_response.json()["access_token"]
auth_header = {"Authorization": token}


@pytest.fixture
def places(demo_db, request) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "places")
    param = getattr(request, "param", None)
    yield collection
    if param:
        for key in param:
            collection.delete_many("name", param["name"])


@pytest.mark.parametrize("places", [new_york], indirect=True)
def test_new_location(places):
    response = requests.post(
        "{0}/location".format(geolocation_host), data=new_york, headers=auth_header
    )
    assert response.status_code == 200
    response = places.get({})
    assert response[0]["name"] == new_york["name"]

    coordinates = response[0]["location"]["coordinates"]
    assert coordinates == [new_york["lng"], new_york["lat"]]


@pytest.mark.parametrize("places", [new_york, jersey_city], indirect=True)
def test_get_near(places):
    places.upsert(
        ObjectId(b"foo-bar-baaz"),
        {
            "name": new_york["name"],
            "location": {
                "type": "Point",
                "coordinates": [new_york["lng"], new_york["lat"]],
            },
        },
    )
    places.upsert(
        ObjectId(b"foo-bar-quux"),
        {
            "name": jersey_city["name"],
            "location": {
                "type": "Point",
                "coordinates": [jersey_city["lng"], jersey_city["lat"]],
            },
        },
    )
    request = requests.get(
        url="{0}/location/{1}/{2}".format(
            geolocation_host, new_york["lat"], new_york["lng"]
        ),
        data={"max_distance": 5000},
        headers=auth_header,
    )
    assert request.status_code == 200
    response = request.json()

    assert response[0]["name"] == new_york["name"]
    assert response[1]["name"] == jersey_city["name"]
