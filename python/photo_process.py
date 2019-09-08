# Note: the image search algorithm is a naive implementation and it's for demo purposes only
import os
import io
import json
import imagehash

from PIL import Image, ImageEnhance
from flasgger import Swagger
from flask import Flask, Response, request


app = Flask(__name__)
swagger = Swagger(app)
storage_path = '/root/storage'


class FileHashSearch:
    hashes = {}

    def load_from_path(self, path: str) -> None:
        for root, subdirs, files in os.walk(path):
            for file in os.listdir(root):
                filePath = os.path.join(root, file)
                hash = imagehash.average_hash(Image.open(filePath))
                print("Loading file: {0}".format(os.path.splitext(file)[0]))
                self.hashes[hash] = os.path.splitext(file)[0]

    def add(self, file, id) -> None:
        self.hashes[imagehash.average_hash(Image.open(file.stream))] = id

    def delete(self, id: int) -> None:
        self.hashes = {k:v for k, v in self.hashes.items() if v != str(id)}

    def get_similar(self, hash, similarity: int = 10):
        return [self.hashes[current_hash] for id, current_hash in enumerate(self.hashes) if hash - current_hash < similarity]


def get_photo_path(photo_id: str):
    return "{0}/{1}.jpg".format(storage_path, str(photo_id))


def get_resized_by_height(img, new_height: int):
    width, height = img.size
    hpercent = (new_height / float(height))
    wsize = int((float(width) * float(hpercent)))
    return img.resize((wsize, new_height), Image.ANTIALIAS)


file_hash_search = FileHashSearch()
file_hash_search.load_from_path(storage_path)



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


@app.route("/photo/similar", methods=["PUT"])
def get_photos_like_this():
    """Find similar photos:
    ---
    parameters:
      - name: file
        required: false
        in: formData
        type: file
      - name: similarity
        in: query
        type: int
        required: false
        maximum: 40
    definitions:
      Number:
        type: int
    responses:
      200:
        description: Found
        schema:
          $ref: '#/definitions/Number'
          type: array
      404:
        description: Erros occured
    """
    if 'file' not in request.files:
        return Response(json.dumps({'error': 'File parameter not present!'}), status=404, mimetype='application/json')
    file = request.files['file']
    if file.mimetype != 'image/jpeg':
        return Response(json.dumps({'error': 'File mimetype must pe jpeg!'}), status=404, mimetype='application/json')
    request_args = request.args
    similarity = int(request.args.get('similarity')) if 'similarity' in request_args else 10
    result = file_hash_search.get_similar(imagehash.average_hash(Image.open(file.stream)), similarity)

    return Response(json.dumps(result), status=200, mimetype='application/json')


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
    file_hash_search.add(file, id)
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
        file_hash_search.delete(id)
    except OSError as e:
        return Response(json.dumps({'error': 'File does not exists!'}), status=404, mimetype='application/json')
    return Response(json.dumps({'status': 'success'}), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)