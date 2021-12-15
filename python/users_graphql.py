from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from flask import Flask
from flask_cors import CORS

from pydantic import BaseModel, Field, validator


app = Flask(__name__)
CORS(app)


class User(BaseModel):
    userid: int
    email: str
    name: str = Field(..., title="Name of the user", max_length=50)


def list_users_resolver(obj, info):
    return {
            "success": True,
            "users": [
                {"userid": 1, "email": "dan.ionescu@gmail.com", "name": "Dan Ionescu"},
                {"userid": 2, "email": "gigi@gmail.com", "name": "Gigi"},
            ]
        }



query = ObjectType("Query")
query.set_field("listUsers", list_users_resolver)

type_defs = load_schema_from_path("python/schema.graphql")
schema = make_executable_schema(
    type_defs, query, snake_case_fallback_resolvers
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)