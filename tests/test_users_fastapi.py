import pytest
import requests
import json
from utils import Collection
from typing import Generator


users_host = "http://localhost:88"
headers = {"accept": "application/json", "Content-Type": "application/json"}
user_id = 100
user_data = {user_id: {"name": "John", "email": "test@email.eu"}}


@pytest.fixture
def users(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "users")
    yield collection
    collection.drop()


@pytest.fixture
def load_users(users):
    users.upsert(user_id, user_data[100])


def test_get_user(load_users):
    response = requests.get(url="{0}/users/100".format(users_host)).json()
    assert response["email"] == user_data[user_id]["email"]
    assert response["name"] == user_data[user_id]["name"]


def test_create_user(users):
    response = requests.post(
        url="{0}/users/{1}".format(users_host, str(user_id)),
        headers=headers,
        data=json.dumps({**user_data[user_id], **{"userid": user_id}}),
    )
    assert response.status_code == 200

    db_response = users.get({})
    assert len(db_response) == 1
    assert db_response[0]["_id"] == user_id
    assert db_response[0]["email"] == user_data[user_id]["email"]
    assert db_response[0]["name"] == user_data[user_id]["name"]


def test_update_user(users, load_users):
    response = requests.put(
        url="{}/users/{}".format(users_host, str(user_id)),
        headers=headers,
        data=json.dumps(
            {**user_data[user_id], **{"userid": user_id, "email": "john@email.com"}}
        ),
    )
    assert response.status_code == 200
    assert response.json()["email"] == "john@email.com"

    db_response = users.get({})
    assert db_response[0] == {"_id": user_id, "name": "John", "email": "john@email.com"}


def test_get_and_delete_users(users, load_users):
    response = requests.get(url="{}/users".format(users_host)).json()
    # look for user before deleting
    assert response == [{**{"userid": user_id}, **user_data[user_id]}]

    requests.delete(url="{}/users/100".format(users_host))
    response = users.get({"_id": 100})
    assert response == []
