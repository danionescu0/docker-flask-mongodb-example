import json, sys

from flask import Flask, request, Response, jsonify
from flask_jwt import JWT, jwt_required
from flasgger import Swagger
from pymongo import MongoClient, GEOSPHERE
from bson import json_util
from werkzeug.security import safe_str_cmp


app = Flask(__name__)
mongo_host = "mongodb"
if len(sys.argv) == 2:
    mongo_host = sys.argv[1]
places = MongoClient(mongo_host, 27017).demo.places

app.config['JWT_AUTH_URL_RULE'] = '/api/auth'
app.config['SECRET_KEY'] = 'super-secret'
app.config["SWAGGER"] = {
    "title": "Swagger JWT Authentiation App",
    "uiversion": 3,
}
app.config['JWT_AUTH_HEADER_PREFIX'] = 'Bearer'

swag = Swagger(app,
    template={
        "info": {
            "title": "Swagger Basic Auth App",
        },
        "consumes": [
            "application/x-www-form-urlencoded",
        ],
        "produces": [
            "application/json",
        ],
    },
)


class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'admin', 'secret'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username: str, password: str):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


jwt = JWT(app, authenticate, identity)


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
        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate(username, password)
        if not user:
            raise Exception("User not found!")

        resp = jsonify({"message": "User authenticated"})
        resp.status_code = 200
        access_token = jwt.jwt_encode_callback(user)
        # add token to response headers - so SwaggerUI can use it
        resp.headers.extend({'jwt-token': access_token})
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
