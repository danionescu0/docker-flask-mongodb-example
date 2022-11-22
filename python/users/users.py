import json

import redis
from datetime import datetime
from flask import Flask, request, Response
from pymongo import MongoClient, errors
from bson import json_util
from flasgger import Swagger
from utils import read_docker_secret
from caching import cache, cache_invalidate


app = Flask(__name__)
swagger = Swagger(app)
users = MongoClient("mongodb", 27017).demo.users


redis_cache = redis.Redis(
    host="redis", port=6379, db=0, password=read_docker_secret("REDIS_PASSWORD")
)


def serialize_datetime(value: str):
    return datetime.strptime(value, "%Y-%m-%d")


def format_user(user: dict) -> dict:
    if user is None:
        return None
    return {
        "userid": user["_id"],
        "name": user["name"],
        "email": user["email"],
        "birthdate": user["birthdate"].strftime("%Y-%m-%d") if "birthdate" in user and user["birthdate"] is not None else None,
        "country": user["country"] if "country" in user else None,
    }

@app.route("/users/<int:userid>", methods=["POST"])
@cache_invalidate(redis=redis_cache, key="userid")
def add_user(userid: int):
    """Create user
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: name
        in: formData
        type: string
        required: true
      - name: birthdate
        in: formData
        type: string
      - name: country
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Creation succeded
    """
    request_params = request.form
    if "email" not in request_params or "name" not in request_params:
        return Response(
            "Email and name not present in parameters!",
            status=404,
            mimetype="application/json",
        )
    try:
        users.insert_one(
            {
                "_id": userid,
                "email": request_params["email"],
                "name": request_params["name"],
                "birthdate": serialize_datetime(request_params["birthdate"]) if "birthdate" in request_params else None,
                "country": request_params["country"],
            }
        )
    except errors.DuplicateKeyError as e:
        return Response("Duplicate user id!", status=404, mimetype="application/json")
    return Response(
        json.dumps(format_user(users.find_one({"_id": userid}))),
        status=200,
        mimetype="application/json",
    )


@app.route("/users/<int:userid>", methods=["PUT"])
@cache_invalidate(redis=redis_cache, key="userid")
def update_user(userid: int):
    """Update user information
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: false
      - name: name
        in: formData
        type: string
        required: false
      - name: birthdate
        in: formData
        type: string
      - name: country
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Update succeded
    """
    request_params = request.form
    set = {}
    if "email" in request_params:
        set["email"] = request_params["email"]
    if "name" in request_params:
        set["name"] = request_params["name"]
    if "birthdate" in request_params:
        set["birthdate"] = serialize_datetime(request_params["birthdate"]),
    if "country" in request_params:
        set["country"] = request_params["country"]

    users.update_one({"_id": userid}, {"$set": set})
    return Response(
        json.dumps(format_user(users.find_one({"_id": userid}))),
        status=200,
        mimetype="application/json",
    )


@app.route("/users/<int:userid>", methods=["GET"])
@cache(redis=redis_cache, key="userid")
def get_user(userid: int):
    """Details about a user
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
    definitions:
      User:
        type: object
        properties:
          _id:
            type: integer
          email:
            type: string
          name:
            type: string
          birthdate:
            type: string
          country:
            type: string
    responses:
      200:
        description: User model
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
    """
    user = users.find_one({"_id": userid})

    if None == user:
        return Response("", status=404, mimetype="application/json")
    print(json.dumps(format_user(user)))
    return Response(json.dumps(format_user(user)), status=200, mimetype="application/json")


@app.route("/users", methods=["GET"])
def get_users():
    """Example endpoint returning all users with pagination
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
      Users:
        type: array
        items:
            properties:
              _id:
                type: integer
              email:
                type: string
              name:
                type: string
              birthdate:
                type: string
              country:
                type: string
    responses:
      200:
        description: List of user models
        schema:
          $ref: '#/definitions/Users'
    """
    request_args = request.args
    limit = int(request_args.get("limit")) if "limit" in request_args else 10
    offset = int(request_args.get("offset")) if "offset" in request_args else 0
    user_list = users.find().limit(limit).skip(offset)
    if None == users:
        return Response(json.dumps([]), status=200, mimetype="application/json")
    extracted = [format_user(d) for d in user_list]

    return Response(
        json.dumps(extracted, default=json_util.default),
        status=200,
        mimetype="application/json",
    )


@app.route("/users/<int:userid>", methods=["DELETE"])
@cache_invalidate(redis=redis_cache, key="userid")
def delete_user(userid: int):
    """Delete operation for a user
    ---
    parameters:
      - name: userid
        in: path
        type: string
        required: true
    responses:
      200:
        description: User deleted
    """
    users.delete_one({"_id": userid})
    return Response("", status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
