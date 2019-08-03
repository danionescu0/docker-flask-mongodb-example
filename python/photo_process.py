import os

import io
from PIL import Image
from flasgger import Swagger
from pymongo import MongoClient
from flask import Flask, Response, request


app = Flask(__name__)
swagger = Swagger(app)
photos = MongoClient('mongo', 27017).demo.photos
storage_path = '/root/storage'


def get_photo_by_id(photo_id):
    return "{0}/{1}.jpg".format(storage_path, str(photo_id))


def get_resized_by_height(img, new_height):
    width, height = img.size
    hpercent = (new_height / float(height))
    wsize = int((float(width) * float(hpercent)))
    return img.resize((wsize, new_height), Image.ANTIALIAS)


@app.route("/photo/<int:id>", methods=["GET"])
def get_photo(id):
    """Returns the photo by id
    parameters:
      - name: id
        in: path
        type: string
        required: true
      - name: resize
        in: query
        type: integer
        required: false
    responses:
      200:
        description: The actual photo
      404:
        description: Photo not found
    """
    request_args = request.args
    resize = int(request_args.get('resize')) if 'resize' in request_args else 0
    try:
        img = Image.open(get_photo_by_id(id))
    except IOError:
        return Response("Error loading image", status=400, mimetype='application/json')
    if resize > 0:
        img = get_resized_by_height(img, resize)
    output = io.BytesIO()
    img.save(output, format='JPEG')
    image_data = output.getvalue()
    output.close()
    return Response(image_data, status=200, mimetype='image/jpeg')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)