import pytest
import requests
import json
import datetime
import dateutil.parser
from typing import Generator
from pytest import FixtureRequest
from utils import Collection, get_random_objectid


headers = {"accept": "application/json", "Content-Type": "application/json"}
book_collection_host = "http://web-book-collection:5000"
books = [
    {
        "isbn": "978-1607965503",
        "name": "Lincoln the Unknown",
        "author": "Dale Carnegie",
        "publisher": "snowballpublishing",
        "nr_available": 5,
    },
    {
        "isbn": "9780262529624",
        "name": "Intro to Computation and Programming using Python",
        "author": "John Guttag",
        "publisher": "MIT Press",
        "nr_available": 3,
    },
]


@pytest.fixture
def book_collection(
    demo_db, request: FixtureRequest
) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "bookcollection")
    yield collection
    collection.delete_many()


@pytest.fixture
def load_books(book_collection):
    for book in books:
        book_collection.upsert(get_random_objectid(), book)


def test_book_add(book_collection):
    responses = list()
    for counter in range(0, len(books)):
        response = requests.put(
            url="{0}/book/{1}".format(book_collection_host, books[counter]["isbn"]),
            headers=headers,
            data=json.dumps(books[counter]),
        )
        assert response.status_code == 200
        responses.append(response)

    assert all([response.status_code == 200 for response in responses])

    db_response = book_collection.get({})
    assert len(db_response) == len(books)

    # assert authors
    authors = [book["author"] for book in books]
    expected_authors = [book["author"] for book in db_response]
    assert authors == expected_authors


def test_get_book(load_books):
    response = requests.get(
        url="{0}/book/{1}".format(book_collection_host, books[0]["isbn"]),
    )
    assert response.status_code == 200
    assert response.json() in books


def test_list_all_books(load_books):
    # check with limit=1
    limit, offset = 1, 0
    response = requests.get(
        url="{0}/book?limit={limit}&offset={offset}".format(
            book_collection_host, limit=limit, offset=offset
        ),
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 1
    assert response[0] == books[0]

    # check with limit=2
    limit, offset = 2, 0
    response = requests.get(
        url="{0}/book?limit={limit}&offset={offset}".format(
            book_collection_host, limit=limit, offset=offset
        ),
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 2
    assert response == books


def test_delete_book(load_books, book_collection):
    assert len(book_collection.get({})) == len(books)
    response = requests.delete(
        url="{0}/book/{1}".format(book_collection_host, books[0]["isbn"]),
        headers=headers,
    )
    assert response.status_code == 200
    # after delete
    assert len(book_collection.get({})) == len(books) - 1


#
#
#
# borrow tests
#
#
#

users = {
    100: {"name": "John", "email": "john@email.com"},
    101: {"name": "Doe", "email": "doe@email.com"},
}

return_days = 10
max_return_days = 20
today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

borrow_data = [
    {
        "id": "1",
        "userid": 100,
        "isbn": books[0]["isbn"],
        "borrow_date": today_date,
        "return_date": today_date + datetime.timedelta(days=return_days),
        "max_return_date": today_date + datetime.timedelta(days=max_return_days),
    },
    {
        "id": "2",
        "userid": 100,
        "isbn": books[1]["isbn"],
        "borrow_date": today_date,
        "return_date": today_date + datetime.timedelta(days=return_days),
        "max_return_date": today_date + datetime.timedelta(days=max_return_days),
    },
    {
        "id": "3",
        "userid": 101,
        "isbn": books[1]["isbn"],
        "borrow_date": today_date,
        "max_return_date": today_date + datetime.timedelta(days=max_return_days),
    },
]


@pytest.fixture
def users_collection(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "users")
    yield collection
    collection.drop()


@pytest.fixture
def load_users(users_collection):
    for user in users:
        users_collection.upsert(user, users[user])


@pytest.fixture
def borrow_collection(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "borrowcollection")
    yield collection
    collection.drop()


@pytest.fixture
def load_book_borrows(borrow_collection):
    for borrow in borrow_data:
        borrow_collection.upsert(get_random_objectid(), borrow)


def test_borrow_book(load_users, load_books, borrow_collection, book_collection):
    data = {
        "id": "1",
        "userid": 100,
        "isbn": books[0]["isbn"],
        "borrow_date": str(today_date),
        "return_date": str(today_date + datetime.timedelta(days=return_days)),
        "max_return_date": str(today_date + datetime.timedelta(days=max_return_days)),
    }
    response = requests.put(
        url="{}/borrow/{}".format(book_collection_host, str(data["userid"])),
        headers=headers,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    db_response = borrow_collection.get({})[0]
    db_response["isbn"] = data["isbn"]
    db_response["userid"] = data["userid"]
    db_response["return_date"] = dateutil.parser.parse(data["return_date"])
    db_response["borrow_date"] = dateutil.parser.parse(data["borrow_date"])
    db_response["max_return_date"] = dateutil.parser.parse(data["max_return_date"])

    # check one less in book collection
    assert book_collection.get({})[0]["nr_available"] == books[0]["nr_available"] - 1


def test_list_a_book_borrow(load_book_borrows, load_books, load_users):
    response = requests.get(url="{}/borrow/{}".format(book_collection_host, "1"))
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["book_name"] == books[0]["name"]
    assert response_json["user_name"] == users[100]["name"]
    assert response_json["borrow_date"] == str(borrow_data[0]["borrow_date"])
    assert response_json["book_author"] == books[0]["author"]


def test_book_borrows(load_book_borrows, load_books):
    limit, offset = 1, 0
    response = requests.get(
        url="{0}/borrow?limit={limit}&offset={offset}".format(
            book_collection_host, limit=limit, offset=offset
        ),
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 1
    assert response[0]["isbn"] in [book["isbn"] for book in books]
    assert isinstance(
        dateutil.parser.parse(response[0]["max_return_date"]), (datetime.datetime)
    )

    limit, offset = 2, 0
    response = requests.get(
        url="{0}/borrow?limit={limit}&offset={offset}".format(
            book_collection_host, limit=limit, offset=offset
        ),
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 2


def test_return_book(load_book_borrows, load_books, book_collection, borrow_collection):
    book_collection.get({})
    return_date = str(today_date + datetime.timedelta(days=4))
    response = requests.put(
        url="{}/borrow/return/{}".format(book_collection_host, "3"),
        headers=headers,
        data=json.dumps({"id": "3", "return_date": return_date}),
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["id"] == "3"
    assert response_json["return_date"] == return_date
    assert book_collection.get({})[1]["nr_available"] == books[1]["nr_available"] + 1
