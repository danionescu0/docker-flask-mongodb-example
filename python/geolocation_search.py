import os, json, time

from flask import Flask, request, Response
from pymongo import MongoClient, GEOSPHERE

from bson import json_util


app = Flask(__name__)
time.sleep(5) # hack for the mongoDb database to get running
places = MongoClient('mongo', 27017).demo.places


@app.route("/location", methods=["POST"])
def new_location():
    request_params = request.form
    if 'name' not in request_params or 'lat' not in request_params or 'lng' not in request_params:
        return Response('Name, lat, lng must be present in parameters!', status=404, mimetype='application/json')
    places.insert_one({
        'name': request_params['name'],
        'location': {'type': 'Point', 'coordinates': [float(request_params['lat']), float(request_params['lng'])]}
    })

    return Response('', status=200, mimetype='application/json')

@app.route("/location/<string:lat>/<string:lng>")
def get_near(lat, lng):
    max_distance = int(request.args.get('max_distance', 10000))
    limit = int(request.args.get('limit', 10))
    cursor = places.find(
        {'location':
             {'$near':
                  {
                      '$geometry': {'type': 'Point',  'coordinates': [float(lat), float(lng)]},
                      '$maxDistance': max_distance
                  }
              }
        }
    ).limit(limit)
    extracted = [{'name': d['name'], 'lat': d['location']['coordinates'][0], 'lng': d['location']['coordinates'][1]}
                 for d in cursor]

    return Response(json.dumps(extracted, default=json_util.default), status=200, mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    places.create_index([('location', GEOSPHERE)], name='location_index')
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=port)