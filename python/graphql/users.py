import sys

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    graphql_sync,
    snake_case_fallback_resolvers,
    ObjectType,
)
from ariadne.constants import PLAYGROUND_HTML
from ariadne import ScalarType
from pymongo import MongoClient
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
mongo_host = "mongodb"
if len(sys.argv) == 2:
    mongo_host = sys.argv[1]
users = MongoClient(mongo_host, 27017).demo.users
datetime_scalar = ScalarType("Date")


@datetime_scalar.serializer
def serialize_datetime(value: str):
    return datetime.strptime(value, "%Y-%m-%d")


class User(BaseModel):
    userid: int
    email: str
    name: str = Field(..., title="Name of the user", max_length=50)
    birth_date: Optional[datetime]
    country: Optional[str] = Field(..., title="Country of origin", max_length=50)

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d")}


def list_users_resolver(obj, info) -> dict:
    user_list = users.find()
    user_list = user_list if None != user_list else []
    formatted = [
        {
            "userid": d["_id"],
            "name": d["name"],
            "email": d["email"],
            "birth_date": d["birth_date"],
            "country": d["country"],
        }
        for d in user_list
    ]
    return {"success": True, "users": formatted}


def upsert_user_resolver(
    obj, info, userid: int, email: str, name: str, birth_date: datetime, country: str
) -> dict:
    try:
        payload = {
            "success": True,
            "user": {
                "_id": userid,
                "email": email,
                "name": name,
                "birth_date": birth_date,
                "country": country,
            },
        }
        users.update_one(
            {"_id": userid},
            {
                "$set": {
                    "email": email,
                    "name": name,
                    "birth_date": birth_date,
                    "country": country,
                }
            },
            upsert=True,
        )
    except ValueError:  # date format errors
        payload = {"success": False, "errors": ["errors"]}
    return payload


def get_user_resolver(obj, info, userid) -> dict:
    try:
        user_data = users.find_one({"_id": userid})
        user_data["userid"] = user_data["_id"]
        payload = {"success": True, "user": user_data}

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"Todo item matching id {id} not found"],
        }
    return payload


def delete_user_resolver(obj, info, userid: int) -> dict:
    try:
        user = users.find_one({"_id": userid})
        users.delete_one({"_id": userid})
        payload = {"success": True, "user": user}
    except AttributeError:
        payload = {"success": False, "errors": ["Not found"]}
    return payload


query = ObjectType("Query")
mutation = ObjectType("Mutation")

query.set_field("listUsers", list_users_resolver)
query.set_field("getUser", get_user_resolver)
mutation.set_field("upsertUser", upsert_user_resolver)
mutation.set_field("deleteUser", delete_user_resolver)

# for prod
type_defs = load_schema_from_path("graphql/schema.graphql")
# for dev uncomment
# type_defs = load_schema_from_path("python/graphql/schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers, datetime_scalar
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
