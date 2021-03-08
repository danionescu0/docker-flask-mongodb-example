import json

from flask import Flask, request, Response
from flasgger import Swagger
from pymongo import MongoClient, GEOSPHERE
from bson import json_util


app = Flask(__name__)
swagger = Swagger(app)
places = MongoClient("mongodb", 27017).demo.places


@app.route("/location", methods=["POST"])
def new_location():
    """Add a place (name, latitude and longitude)
    ---
    parameters:
      - name: name
        in: formData
        type: string
        required: true
      - name: lat
        in: formData
        type: string
        required: true
      - name: lng
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Place added
    """
    request_params = request.form
    if (
        "name" not in request_params
        or "lat" not in request_params
        or "lng" not in request_params
    ):
        return Response(
            "Name, lat, lng must be present in parameters!",
            status=404,
            mimetype="application/json",
        )
    latitude = float(request_params["lng"])
    longitude = float(request_params["lat"])
    places.insert_one(
        {
            "name": request_params["name"],
            "location": {"type": "Point", "coordinates": [latitude, longitude]},
        }
    )
    return Response(
        json.dumps({"name": request_params["name"], "lat": latitude, "lng": longitude}),
        status=200,
        mimetype="application/json",
    )


@app.route("/location/<string:lat>/<string:lng>")
def get_near(lat, lng):
    """Get all points near a location given coordonates, and radius
    ---
    parameters:
      - name: lat
        in: path
        type: string
        required: true
      - name: lng
        in: path
        type: string
        required: true
      - name: max_distance
        in: query
        type: integer
        required: false
      - name: limit
        in: query
        type: integer
        required: false
    definitions:
      Place:
        type: object
        properties:
          name:
            type: string
          lat:
            type: double
          long:
            type: double
    responses:
      200:
        description: Places list
        schema:
          $ref: '#/definitions/Place'
          type: array
    """
    max_distance = int(request.args.get("max_distance", 10000))
    limit = int(request.args.get("limit", 10))
    cursor = places.find(
        {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(lng), float(lat)],
                    },
                    "$maxDistance": max_distance,
                }
            }
        }
    ).limit(limit)
    extracted = [
        {
            "name": d["name"],
            "lat": d["location"]["coordinates"][1],
            "lng": d["location"]["coordinates"][0],
        }
        for d in cursor
    ]
    return Response(
        json.dumps(extracted, default=json_util.default),
        status=200,
        mimetype="application/json",
    )


if __name__ == "__main__":
    # cretes a GEOSHPHERE (2dsphere in MongoDb: https://docs.mongodb.com/manual/core/2dsphere/) index
    # named "location_index" on "location" field, it's used to search by distance
    places.create_index([("location", GEOSPHERE)], name="location_index")

    # starts the app in debug mode, bind on all ip's and on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
