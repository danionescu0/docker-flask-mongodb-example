import pytest, requests

from utils import MongoDb


users_host = "http://localhost:81"


@pytest.fixture
def collection():
    con = MongoDb(host="localhost")
    con.create_connection()
    con.set_collection("users")
    yield con
    con.drop()


def test_get_user(collection):
    collection.upsert(100, {"name": "John", "email": "test@email.eu"})
    response = requests.get(url="{0}/users/100".format(users_host)).json()
    assert response["_id"] == 100
    assert response["email"] == "test@email.eu"
    assert response["name"] == "John"


def test_create_user(collection):
    requests.put(
        url="{0}/users/101".format(users_host),
        data={"name": "John Doe", "email": "johny@email.eu"},
    ).json()

    response = collection.get({"_id": 101})
    assert len(response) == 1
    assert response[0]["_id"] == 101
    assert response[0]["email"] == "johny@email.eu"
    assert response[0]["name"] == "John Doe"


def test_update_user(collection):
    collection.upsert(100, {"name": "John", "email": "test@email.eu"})
    requests.post(
        url="{0}/users/100".format(users_host),
        data={"name": "John", "email": "john@email.com"},
    ).json()
    response = collection.get({"_id": 100})

    assert response[0] == {"_id": 100, "name": "John", "email": "john@email.com"}


def test_get_and_delete_users(collection):
    collection.upsert(100, {"name": "John", "email": "john@email.com"})
    collection.upsert(101, {"name": "Doe", "email": "doe@email.com"})
    response = requests.get(url="{}/users".format(users_host)).json()
    # testing get request
    assert response == [
        {"userid": 100, "name": "John", "email": "john@email.com"},
        {"userid": 101, "name": "Doe", "email": "doe@email.com"},
    ]

    requests.delete(url="{}/users/100".format(users_host))
    response = collection.get({"_id": 100})
    # asserting the delete has been done
    assert response == []
