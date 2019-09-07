import os

import io
import json
from PIL import Image, ImageEnhance
from flasgger import Swagger
from flask import Flask, Response, request


app = Flask(__name__)
swagger = Swagger(app)
storage_path = '/root/storage'


def get_photo_path(photo_id):
    return "{0}/{1}.jpg".format(storage_path, str(photo_id))


def get_resized_by_height(img, new_height):
    width, height = img.size
    hpercent = (new_height / float(height))
    wsize = int((float(width) * float(hpercent)))
    return img.resize((wsize, new_height), Image.ANTIALIAS)


@app.route("/photo/<int:id>", methods=["GET"])
def get_photo(id):
    """Returns the photo by id
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
      - name: resize
        in: query
        type: integer
        required: false
      - name: rotate
        in: query
        type: integer
        required: false
      - name: brightness
        in: query
        type: float
        required: false
        maximum: 20
    responses:
      200:
        description: The actual photo
      404:
        description: Photo not found
    """
    request_args = request.args
    resize = int(request_args.get('resize')) if 'resize' in request_args else 0
    rotate = int(request.args.get('rotate')) if 'rotate' in request_args else 0
    brightness = float (request.args.get('brightness')) if 'brightness' in request_args else 0
    if brightness > 20:
        return Response("Maximum value for brightness is 20", status=404, mimetype='application/json')

    try:
        img = Image.open(get_photo_path(id))
    except IOError:
        return Response(json.dumps({'error': 'Error loading image'}), status=404, mimetype='application/json')
    if resize > 0:
        img = get_resized_by_height(img, resize)
    if rotate > 0:
        img = img.rotate(rotate)
    if brightness > 0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    output = io.BytesIO()
    img.save(output, format='JPEG')
    image_data = output.getvalue()
    output.close()
    return Response(image_data, status=200, mimetype='image/jpeg')


@app.route("/photo/<int:id>", methods=["PUT"])
def set_photo(id):
    """Add jpeg photo on disk:
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
      - name: file
        required: false
        in: formData
        type: file
    responses:
      200:
        description: Added succesfully
      404:
        description: Error saving photo
    """
    if 'file' not in request.files:
        return Response(json.dumps({'error': 'File parameter not present!'}), status=404, mimetype='application/json')
    file = request.files['file']
    if file.mimetype != 'image/jpeg':
        return Response(json.dumps({'error': 'File mimetype must pe jpeg!'}), status=404, mimetype='application/json')
    try:
        file.save(get_photo_path(id))
    except Exception as e:
        return Response(json.dumps({'error': 'Could not save file to disk!'}), status=404, mimetype='application/json')
    return Response(json.dumps({'status': 'success'}), status=200, mimetype='application/json')


@app.route("/photo/<int:id>", methods=["DELETE"])
def delete_photo(id):
    """Delete photo by id:
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Deleted succesfully
      404:
        description: Error deleting
    """
    try:
        os.remove(get_photo_path(id))
    except OSError as e:
        return Response(json.dumps({'error': 'File does not exists!'}), status=404, mimetype='application/json')
    return Response(json.dumps({'status': 'success'}), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)