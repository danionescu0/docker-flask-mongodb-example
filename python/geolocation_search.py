import json, sys

from flask import Flask, request, Response, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from pymongo import MongoClient, GEOSPHERE
from bson import json_util
from flask_restful import Api


app = Flask(__name__)
mongo_host = "mongodb"
if len(sys.argv) == 2:
    mongo_host = sys.argv[1]
places = MongoClient(mongo_host, 27017).demo.places

app.config["JWT_AUTH_URL_RULE"] = "/api/auth"
app.config["JWT_SECRET_KEY"] = "super-secret"

template = {
  "swagger": "2.0",
  "info": {
    "title": "Geolocation search demo",
    "description": "A demo of geolocation search using mongodb and flask",
  },
  "securityDefinitions": {
    "Bearer": {
      "type": "apiKey",
      "name": "Authorization",
      "in": "header",
      "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
    }
  },
  "security": [
    {
      "Bearer": [ ],
    }
  ]
}

app.config['SWAGGER'] = {
    'title': 'Geolocation search demo',
    'uiversion': 3,
    "specs_route": "/apidocs/"
}
swagger = Swagger(app, template=template)
api = Api(app)


class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, "admin", "secret"),
]

jwt = JWTManager(app)


@app.route("/login", methods=["POST"])
def login():
    """
    User authenticate method.
    ---
    description: Authenticate user with supplied credentials.
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: User successfully logged in.
      400:
        description: User login failed.
    """
    try:
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        authenticated_user = [user for user in users if username==user.username and password==user.password]
        if not authenticated_user:
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity=username)
        resp = jsonify(access_token="Bearer {0}".format(access_token))
    except Exception as e:
        resp = jsonify({"message": "Bad username and/or password"})
        resp.status_code = 401
    return resp


@app.route("/location", methods=["POST"])
@jwt_required()
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
@jwt_required()
def get_near(lat: str, lng: str):
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
