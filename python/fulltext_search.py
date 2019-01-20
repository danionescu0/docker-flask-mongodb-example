import os, json, datetime, time

from flask import Flask, request, Response
from pymongo import MongoClient, TEXT
from bson import json_util


app = Flask(__name__)
time.sleep(5) # hack for the mongoDb database to get running
fulltext_search = MongoClient('mongo', 27017).demo.fulltext_search


@app.route("/fulltext", methods=["PUT"])
def add_expression():
    request_params = request.form
    if 'expression' not in request_params and 'name' not in request_params:
        return Response('"Expression" must be present as a POST parameter!', status=404, mimetype='application/json')
    fulltext_search.save(
            {
                'app_text': request_params['expression'],
                'indexed_date': datetime.datetime.utcnow()
            }
    )

    return Response({}, status=200, mimetype='application/json')


@app.route("/search/<string:searched_expression>")
def search(searched_expression):
    results = fulltext_search.find(
        {
            '$text': {'$search': searched_expression}
        },
        {
            'score': {'$meta': 'textScore'}
        }
    ).sort([
        ('score', {'$meta': 'textScore'})
    ]).limit(10)
    results = [{'text': result['app_text'], 'date': result['indexed_date'].isoformat()} for result in results]

    return Response(json.dumps(list(results), default=json_util.default), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.config['DEBUG'] = True
    #first create the fulltext index
    fulltext_search.create_index([('app_text', TEXT)], name='fulltextsearch_index', default_language='english')
    #then run the app
    app.run(host='0.0.0.0', port=port)