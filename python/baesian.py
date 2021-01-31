import json

from flask import Flask, request, Response
from pymongo import MongoClient
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
baesian = MongoClient('mongodb', 27017).demo.baesian


@app.route("/item/<int:itemid>", methods=["POST"])
def upsert_item(itemid):
    """Create item
    ---
    parameters:
      - name: itemid
        in: path
        type: string
        required: true
      - name: name
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Item added
    """
    request_params = request.form
    if 'name' not in request_params:
        return Response('Name not present in parameters!', status=404, mimetype='application/json')
    baesian.update_one(
        {'_id': itemid},
        {'$set':
             {'name': request_params['name'], 'nr_votes': 0}
        },
        upsert=True
    )

    return Response(json.dumps({"_id": itemid, 'name': request_params['name']}), status=200, mimetype='application/json')


@app.route("/item/vote/<int:itemid>", methods=["PUT"])
def add_vote(itemid):
    """Vote an item
    ---
    parameters:
      - name: itemid
        in: path
        type: string
        required: true
      - name: mark
        in: formData
        type: integer
        required: false
      - name: userid
        in: formData
        type: integer
        required: false
    responses:
      200:
        description: Update succeded
    """
    request_params = request.form
    if 'mark' not in request_params or 'userid' not in request_params:
        return Response('Mark and userid must be present in form data!', status=404, mimetype='application/json')
    mark = int(request_params['mark'])
    if mark not in range(0, 10):
        return Response('Mark must be in range (0, 10) !', status=500, mimetype='application/json')
    userid = int(request_params['userid'])
    update_items_data = {
        '$push': {'marks': {'userid': userid, 'mark': mark}},
        '$inc': {'nr_votes': 1, 'sum_votes':  mark}
    }
    baesian.update_one({'_id': itemid}, update_items_data)
    return Response('', status=200, mimetype='application/json')


@app.route("/item/<int:itemid>", methods=["GET"])
def get_item(itemid):
    """Item details
    ---
    parameters:
      - name: itemid
        in: path
        type: string
        required: true
    definitions:
      Item:
        type: object
        properties:
          _id:
            type: integer
          name:
            type: string
          marks:
            type: array
            items:
                type: integer
          sum_votes:
            type: integer
          nr_votes:
            type: integer
          baesian_average:
            type: float
    responses:
      200:
        description: Item model
        schema:
          $ref: '#/definitions/Item'
      404:
        description: Item not found
    """
    item_data = baesian.find_one({'_id': itemid})
    if None == item_data:
        return Response("", status=404, mimetype='application/json')
    if 'marks' not in item_data:
        item_data['nr_votes'] = 0
        item_data['sum_votes'] = 0
        item_data['baesian_average'] = 0
        return Response(json.dumps(item_data), status=200, mimetype='application/json')

    average_nr_votes_pipeline = [
            {"$group": {"_id": "avg_nr_votes", "avg_nr_votes": {"$avg": "$nr_votes"}}},
        ]
    average_nr_votes = list(baesian.aggregate(average_nr_votes_pipeline))[0]['avg_nr_votes']
    average_rating = [
            {"$group": {"_id": "avg", "avg": { "$sum": "$sum_votes"}, "count": {"$sum": "$nr_votes"}}},
            {"$project": {"result": {"$divide": ["$avg", "$count"]}}}
        ]
    average_rating = list(baesian.aggregate(average_rating))[0]['result']
    item_nr_votes = item_data['nr_votes']
    item_average_rating = item_data['sum_votes'] / item_data['nr_votes']
    baesian_average = round(((average_nr_votes * average_rating) +
                       (item_nr_votes * item_average_rating)) / (average_nr_votes + item_nr_votes), 3)
    item_data['baesian_average'] = baesian_average
    return Response(json.dumps(item_data), status=200, mimetype='application/json')


@app.route("/items", methods=["GET"])
def get_items():
    """All items with pagination without averages
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
      - name: offset
        in: query
        type: integer
        required: false
    definitions:
      Items:
        type: array
        items:
            properties:
              _id:
                type: integer
              name:
                type: string
              marks:
                type: array
                items:
                    type: integer
    responses:
      200:
        description: List of items
        schema:
          $ref: '#/definitions/Items'
    """
    request_args = request.args
    limit = int(request_args.get('limit')) if 'limit' in request_args else 10
    offset = int(request_args.get('offset')) if 'offset' in request_args else 0
    item_list = baesian.find().limit(limit).skip(offset)
    if None == baesian:
        return Response(json.dumps([]), status=200, mimetype='application/json')
    extracted = [
        {'_id': d['_id'],
         'name': d['name'],
         'marks': d['marks'] if 'marks' in d else []
         } for d in item_list]
    return Response(json.dumps(extracted), status=200, mimetype='application/json')


@app.route("/item/<int:itemid>", methods=["DELETE"])
def delete_item(itemid):
    """Delete operation for a item
    ---
    parameters:
      - name: itemid
        in: path
        type: string
        required: true
    responses:
      200:
        description: Item deleted
    """
    baesian.delete_one({'_id': itemid})
    return Response('', status=200, mimetype='application/json')


if __name__ == "__main__":
    # starts the app in debug mode, bind on all ip's and on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)