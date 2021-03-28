import pytest
import requests
from typing import Generator
import json
from utils import Collection


host = "http://localhost:86"


book = {
    "name": "Intro to Computation and Programming using Python",
    "isbn": "9780262529624",
    "author": "John Guttag",
    "publisher": "MIT Press",
    "nr_available": 3,
}


def test_put():
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    resp = requests.put(
        "http://localhost:86/book/{}".format(book["isbn"]),
        headers=headers,
        data=json.dumps(book),
    )
    print(json.dumps(book))
    print(resp.status_code)
    print(resp.content)
