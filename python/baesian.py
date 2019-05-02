import os, json, time


from flask import Flask, request, Response
from pymongo import MongoClient, errors
from bson import json_util
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
time.sleep(5) # hack for the mongoDb database to get running
# baesian = MongoClient('mongo', 27017).demo.baesian
baesian = MongoClient('localhost', 27017).demo.baesian




@app.route("/item/<int:itemid>", methods=["POST"])
def upsert_item(itemid):
    """Update item information
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
        description: Update succeded
    """
    request_params = request.form
    if 'name' not in request_params:
        return Response('Name not present in parameters!', status=404, mimetype='application/json')
    baesian.update_one({'_id': itemid}, {'$set': {'name': request_params['name']}}, upsert = True)

    return Response('', status=200, mimetype='application/json')

@app.route("/item/vote/<int:itemid>", methods=["PUT"])
def add_vote(itemid):
    request_params = request.form
    print(request_params)
    if 'mark' not in request_params or 'userid' not in request_params:
        return Response('Mark and userid must be present in form data!', status=404, mimetype='application/json')
    update_data = {
        '$push': {'marks': {'userid': request_params['userid'], 'mark': request_params['mark']}}
    }
    baesian.update_one({'_id': itemid}, update_data)
    return Response('', status=200, mimetype='application/json')


@app.route("/item/<int:itemid>", methods=["GET"])
def get_item(itemid):
    def get_user(itemid):
        """Example endpoint returning details about an item
        ---
        parameters:
          - name: userid
            in: path
            type: string
            required: true

        """
    user = baesian.find_one({'_id': itemid})
    if None == user:
        return Response("", status=404, mimetype='application/json')

    return Response(json.dumps(user), status=200, mimetype='application/json')



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)