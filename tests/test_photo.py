import pytest, requests
from typing import Generator


photo_host = "http://localhost:5000"
filepath = "./tests/resources/test.jpg"


def test_put_photo():
    test_file = ("test.jpg", open(filepath, "rb"), "image/jpeg")
    response = requests.put(
        url="{0}/photo/101".format(photo_host), files={"file": test_file}
    ).json()
    print(response)
