import random, os, json, datetime, time

from flask import Flask, Response, request
from flasgger import Swagger
from pymongo import MongoClient
from bson import json_util


app = Flask(__name__)
swagger = Swagger(app)
time.sleep(5) # hack for the mongoDb database to get running
random_numbers = MongoClient('mongo', 27017).demo.random_numbers


@app.route("/random", methods=["PUT"])
def random_generator():
    """Add a number number to the list of last 5 numbers
    ---
    parameters:
      - name: lower
        in: formData
        type: int32
        required: false
      - name: upper
        in: formData
        type: int32
        required: false
    responses:
      200:
        description: Random number added succesfully
        type: int
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
    extracted = [d['value'] for d in last_numbers[0]['items']]

    return Response(json.dumps(extracted, default=json_util.default), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)