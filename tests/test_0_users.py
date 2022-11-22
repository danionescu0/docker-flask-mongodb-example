import pytest, requests
from datetime import datetime
from utils import Collection
from typing import Generator


users_host = "http://web-users:5000"
# @todo run this test on users fastapi too with pytest.mark.parametrize


@pytest.fixture
def users(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "users")
    yield collection
    collection.drop()


def test_get_user(users):
    users.upsert(120,
                 {
                        "name": "John",
                        "email": "test@email.eu",
                        "birthdate": datetime.strptime("1983-11-28", '%Y-%m-%d'),
                        "country": "Romania"
                    }
                 )
    response = requests.get(url="{0}/users/120".format(users_host)).json()
    print(response)
    assert response["userid"] == 120
    assert response["email"] == "test@email.eu"
    assert response["name"] == "John"
    assert response["birthdate"] == "1983-11-28"
    assert response["country"] == "Romania"


def test_create_user(users):
    response = requests.post(
        url="{0}/users/101".format(users_host),
        data={
            "name": "John Doe",
            "email": "johny@email.eu",
            "birthdate": "1984-11-28",
            "country": "Russia"
        },
    )
    assert response.status_code == 200

    response = users.get({"_id": 101})
    print(response)
    assert len(response) == 1
    assert response[0]["_id"] == 101
    assert response[0]["email"] == "johny@email.eu"
    assert response[0]["name"] == "John Doe"
    assert response[0]["birthdate"].strftime('%Y-%m-%d') == "1984-11-28"
    assert response[0]["country"] == "Russia"


def test_update_user(users):
    users.upsert(110, {"name": "John", "email": "test@email.eu"})
    requests.put(
        url="{0}/users/110".format(users_host),
        data={"name": "John", "email": "john@email.com"},
    ).json()
    response = users.get({"_id": 110})
    assert response[0] == {"_id": 110, "name": "John", "email": "john@email.com"}


def test_get_and_delete_users(users):
    users.upsert(105, {"name": "John", "email": "john@email.com"})
    users.upsert(109, {"name": "Doe", "email": "doe@email.com"})
    response = requests.get(url="{}/users".format(users_host)).json()
    # testing get request
    print(response)
    assert response == [
        {"userid": 105, "name": "John", "email": "john@email.com", 'birthdate': None, 'country': None},
        {"userid": 109, "name": "Doe", "email": "doe@email.com", 'birthdate': None, 'country': None},
    ]

    requests.delete(url="{}/users/105".format(users_host))
    response = users.get({"_id": 105})
    # asserting the delete has been done
    assert response == []
