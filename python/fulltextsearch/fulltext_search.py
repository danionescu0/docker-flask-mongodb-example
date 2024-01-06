import sys
import json, datetime

from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from werkzeug import generate_password_hash, check_password_hash
from flasgger import Swagger
from pymongo import MongoClient, TEXT
from bson import json_util


app = Flask(__name__)
auth = HTTPBasicAuth()
swagger_template = {"securityDefinitions": {"basicAuth": {"type": "basic"}}}
users = {
    "admin": generate_password_hash("changeme"),
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


swagger = Swagger(app, template=swagger_template)
mongo_host = "mongodb"
if len(sys.argv) == 2:
    mongo_host = sys.argv[1]
fulltext_search = MongoClient(mongo_host, 27017).demo.fulltext_search


@app.route("/search/<string:searched_expression>")
@auth.login_required
def search(searched_expression: str):
    """Search by an expression
    ---
    parameters:
      - name: searched_expression
        in: path
        type: string
        required: true
    definitions:
      Result:
        type: object
        properties:
          app_text:
            type: string
          indexed_date:
            type: date
    responses:
      200:
        description: List of results
        schema:
          $ref: '#/definitions/Result'
    """
    results = (
        fulltext_search.find(
            {"$text": {"$search": searched_expression}},
            {"score": {"$meta": "textScore"}},
        )
        .sort([("score", {"$meta": "textScore"})])
        .limit(10)
    )
    results = [
        {"text": result["app_text"], "date": result["indexed_date"].isoformat()}
        for result in results
    ]
    return Response(
        json.dumps(list(results), default=json_util.default),
        status=200,
        mimetype="application/json",
    )


@app.route("/fulltext", methods=["PUT"])
@auth.login_required
def add_expression():
    """Add an expression to fulltext index
    ---
    parameters:
      - name: expression
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Creation succeded
    """
    request_params = request.form
    if "expression" not in request_params:
        return Response(
            '"Expression" must be present as a POST parameter!',
            status=404,
            mimetype="application/json",
        )
    document = {
        "app_text": request_params["expression"],
        "indexed_date": datetime.datetime.utcnow(),
    }
    fulltext_search.save(document)
    return Response(
        json.dumps(document, default=json_util.default),
        status=200,
        mimetype="application/json",
    )


if __name__ == "__main__":
    # create the fulltext index
    fulltext_search.create_index(
        [("app_text", TEXT)], name="fulltextsearch_index", default_language="english"
    )
    # starts the app in debug mode, bind on all ip's and on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
