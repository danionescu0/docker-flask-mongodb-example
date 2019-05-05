import os, json, time


from flask import Flask, request, Response
from pymongo import MongoClient, errors
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
baesian = MongoClient('mongo', 27017).demo.baesian


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
    baesian.update_one({'_id': itemid}, {'$set': {'name': request_params['name']}}, upsert = True)

    return Response('', status=200, mimetype='application/json')


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
        type: int
        required: false
      - name: userid
        in: formData
        type: int
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
            type: int32
          name:
            type: string
          marks:
            type: array
          sum_votes: int32
          nr_votes: int32
          baesian_average: float
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
    print(average_rating, item_average_rating, item_data)

    return Response(json.dumps(item_data), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)