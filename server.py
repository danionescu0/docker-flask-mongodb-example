from flask import Flask
from pymongo import MongoClient
import random, os, json, datetime
from bson import json_util

app = Flask(__name__)
random_collection = MongoClient('mongo', 27017).randomia.numbers

@app.route("/random/<int:lower>/<int:upper>")
def random_generator(lower, upper):
    number = str(random.randint(lower, upper))
    random_collection.update(
        {"_id" : "lasts"},
        {"$push" : {
            "items" : {
                "$each": [{"value" : number, "date": datetime.datetime.utcnow()}],
                "$sort" : {"date" : -1},
                "$slice" : 5
            }
        }},
        upsert = True
    )

    return number

@app.route("/random-list")
def last_number_list():
    last_numbers = list(random_collection.find({"_id" : "lasts"}))
    extracted = [d['value'] for d in last_numbers[0]['items']]

    return json.dumps(extracted, default=json_util.default)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=port)