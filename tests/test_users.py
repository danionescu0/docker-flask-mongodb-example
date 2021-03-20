import pytest, requests
from utils import Collection
from typing import Generator


users_host = "http://localhost:81"


@pytest.fixture
def users(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "users")
    yield collection
    collection.drop()


def test_get_user(users):
    users.upsert(100, {"name": "John", "email": "test@email.eu"})
    response = requests.get(url="{0}/users/100".format(users_host)).json()
    assert response["_id"] == 100
    assert response["email"] == "test@email.eu"
    assert response["name"] == "John"


def test_create_user(users):
    requests.put(
        url="{0}/users/101".format(users_host),
        data={"name": "John Doe", "email": "johny@email.eu"},
    ).json()

    response = users.get({"_id": 101})
    assert len(response) == 1
    assert response[0]["_id"] == 101
    assert response[0]["email"] == "johny@email.eu"
    assert response[0]["name"] == "John Doe"


def test_update_user(users):
    users.upsert(100, {"name": "John", "email": "test@email.eu"})
    requests.post(
        url="{0}/users/100".format(users_host),
        data={"name": "John", "email": "john@email.com"},
    ).json()
    response = users.get({"_id": 100})

    assert response[0] == {"_id": 100, "name": "John", "email": "john@email.com"}


def test_get_and_delete_users(users):
    users.upsert(100, {"name": "John", "email": "john@email.com"})
    users.upsert(101, {"name": "Doe", "email": "doe@email.com"})
    response = requests.get(url="{}/users".format(users_host)).json()
    # testing get request
    assert response == [
        {"userid": 100, "name": "John", "email": "john@email.com"},
        {"userid": 101, "name": "Doe", "email": "doe@email.com"},
    ]

    requests.delete(url="{}/users/100".format(users_host))
    response = users.get({"_id": 100})
    # asserting the delete has been done
    assert response == []
