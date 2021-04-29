import pytest
import requests
import os
from pathlib import Path
from PIL import Image


photo_process_host = "http://localhost:85"
parent_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
image_path = os.path.join(str(parent_path) + "/tests/resources/test.jpg")
storage_path = os.path.join(str(parent_path) + "/container-storage")
image_id = "101"


@pytest.fixture
def set_photo():
    response = requests.put(
        url="{0}/photo/{1}".format(photo_process_host, image_id),
        files={"file": ("test.jpg", open(image_path, "rb"), "image/jpeg")},
    )
    return response


def test_put_photo(set_photo):
    assert set_photo.status_code == 200
    image_storage_path = Path(os.path.join(storage_path, "{}.jpg".format(image_id)))
    assert image_storage_path.exists()

    # cleanup
    image_storage_path.unlink()


def test_get_photo_and_similar(set_photo):
    # get photo resized to 100
    response = requests.get(
        url="{0}/photo/{1}".format(photo_process_host, image_id), data={"resize": 100}
    )
    assert response.status_code == 200
    temp_image_path = os.path.join(str(parent_path) + "/tests/resources/temp.jpg")

    # store the resized photo
    with open(temp_image_path, "wb") as f:
        f.write(response.content)

    im = Image.open(temp_image_path)
    assert im.format == "JPEG"

    # search for photo similar to resized one
    response = requests.put(
        url="{0}/photo/similar".format(photo_process_host),
        files={"file": ("temp.jpg", open(temp_image_path, "rb"), "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.json() == [int(image_id)]

    # cleanup
    os.remove(temp_image_path)


def test_delete_image(set_photo):
    image_storage_path = Path(os.path.join(storage_path, "{}.jpg".format(image_id)))
    assert image_storage_path.exists()

    # delete the image
    requests.delete(url="{0}/photo/{1}".format(photo_process_host, image_id))
    assert image_storage_path.exists() == False
