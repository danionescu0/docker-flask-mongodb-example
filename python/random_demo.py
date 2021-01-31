import random, json, datetime, sys

from flask import Flask, Response, request
from flasgger import Swagger
from pymongo import MongoClient
from bson import json_util

from utils import get_logger


app = Flask(__name__)
swagger = Swagger(app)
mongo_host = 'mongodb'
if len(sys.argv) == 2:
    mongo_host = sys.argv[1]
random_numbers = MongoClient(mongo_host, 27017).demo.random_numbers
logger = get_logger()


@app.route("/random", methods=["PUT"])
def random_insert():
    """Add a number number to the list of last 5 numbers
    ---
    parameters:
      - name: lower
        in: formData
        type: integer
        required: false
      - name: upper
        in: formData
        type: integer
        required: false
    responses:
      200:
        description: Random number added successfully
        type: integer
    """
    request_params = request.form
    number = str(random.randint(int(request_params['lower']), int(request_params['upper'])))
    random_numbers.update(
        {"_id": "lasts"},
        {"$push": {
            "items": {
                "$each": [{"value": number, "date": datetime.datetime.utcnow()}],
                "$sort": {"date": -1},
                "$slice": 5
            }
        }},
        upsert=True
    )
    return Response(number, status=200, mimetype='application/json')

@app.route("/random", methods=["GET"])
def random_generator():
    """Returns a random number in interval
    ---
    parameters:
      - name: lower
        in: query
        type: integer
        required: false
      - name: upper
        in: query
        type: integer
        required: false
    responses:
      200:
        description: Random number generated
        type: integer
    """
    request_args = request.args
    lower = int(request_args.get('lower')) if 'lower' in request_args else 10
    upper = int(request_args.get('upper')) if 'upper' in request_args else 0
    if upper < lower:
        return Response(json.dumps({'error': 'Upper boundary must be greater or equal than lower boundary'}), status=400, mimetype='application/json')
    number = str(random.randint(lower, upper))
    return Response(number, status=200, mimetype='application/json')


@app.route("/random-list")
def last_number_list():
    """Gets the latest 5 generated numbers
    ---
    definitions:
      Number:
        type: int
    responses:
      200:
        description: list of results
        schema:
          $ref: '#/definitions/Number'
          type: array
    """
    last_numbers = list(random_numbers.find({"_id": "lasts"}))
    if len(last_numbers) == 0:
        extracted = []
    else:
        extracted = [d['value'] for d in last_numbers[0]['items']]
    return Response(json.dumps(extracted, default=json_util.default), status=200, mimetype='application/json')


if __name__ == "__main__":
    logger.debug("Random demo app started")
    # starts the app in debug mode, bind on all ip's and on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)