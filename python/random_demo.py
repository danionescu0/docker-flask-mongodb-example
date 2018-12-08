import random, os, json, datetime, time

from flask import Flask, Response
from pymongo import MongoClient
from bson import json_util


app = Flask(__name__)
random_numbers = MongoClient('mongo', 27017).demo.random_numbers

time.sleep(5) # hack for the mongoDb database to get running

@app.route("/random/<int:lower>/<int:upper>")
def random_generator(lower, upper):
    number = str(random.randint(lower, upper))
    random_numbers.update(
        {"_id" : "lasts"},
        {"$push" : {
            "items" : {
                "$each": [{"value" : number, "date": datetime.datetime.utcnow()}],
                "$sort" : {"date" : -1},
                "$slice" : 5
            }
        }},
        upsert=True
    )

    return Response(number, status=200, mimetype='application/json')


@app.route("/random-list")
def last_number_list():
    last_numbers = list(random_numbers.find({"_id" : "lasts"}))
    extracted = [d['value'] for d in last_numbers[0]['items']]

    return Response(json.dumps(extracted, default=json_util.default), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=port)