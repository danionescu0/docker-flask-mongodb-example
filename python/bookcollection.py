import sys
import json
import requests
import dateutil.parser

from flask import Flask, request, Response
from flask_restplus import Api, Resource, fields, reqparse
from pymongo import MongoClient, errors

from utils import get_logger


if len(sys.argv) == 3:
    _, users_host, mongo_host = sys.argv
    mongo_client = MongoClient(mongo_host, 27017)
else:
    users_host = "http://web-users:5000"
    mongo_client = MongoClient("mongodb", 27017)
bookcollection = mongo_client.demo.bookcollection
borrowcollection = mongo_client.demo.borrowcollection
logger = get_logger()


app = Flask(__name__)
api = Api(
    app=app,
    title="Book collection",
    description="Simulates a book library with users and book borrwing",
)
book_api = api.namespace("book", description="Book api")
borrow_api = api.namespace("borrow", description="Boorrow, returing api")

book_model = book_api.model(
    "Book",
    {
        "isbn": fields.String(description="ISBN", required=True),
        "name": fields.String(description="Name of the book", required=True),
        "author": fields.String(description="Book author", required=True),
        "publisher": fields.String(description="Book publisher", required=True),
        "nr_available": fields.Integer(
            min=0, description="Nr books available for lend", required=True
        ),
    },
)

borrow_model = borrow_api.model(
    "Borrow",
    {
        "id": fields.String(
            min=0, description="Unique uuid for borrowing", required=True
        ),
        "userid": fields.Integer(
            min=0, description="Userid of the borrower", required=True
        ),
        "isbn": fields.String(description="ISBN", required=True),
        "borrow_date": fields.DateTime(required=True),
        "return_date": fields.DateTime(required=False),
        "max_return_date": fields.DateTime(required=True),
    },
)

return_model = borrow_api.model(
    "Return",
    {
        "id": fields.String(
            min=0, description="Unique uuid for borrowing", required=True
        ),
        "return_date": fields.DateTime(required=False),
    },
)


class User:
    def __init__(self, exists: bool, userid: int, name: str, email: str) -> None:
        self.exists = exists
        self.userid = userid
        self.name = name
        self.email = email


pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("limit", type=int, help="Limit")
pagination_parser.add_argument("offset", type=int, help="Offset")


def get_user(id: int) -> User:
    try:
        response = requests.get(url="{0}/users/{1}".format(users_host, str(id)))
    except Exception as e:
        logger.error("Error getting user data error: {0}".format(str(e)))
        return User(False, id, None, None)
    if response.status_code != 200:
        return User(False, id, None, None)
    try:
        result = response.json()
        return User(True, id, result["name"], result["email"])
    except:
        return User(False, id, None, None)


@borrow_api.route("/return/<string:id>")
class Return(Resource):
    @borrow_api.doc(responses={200: "Ok"})
    @borrow_api.expect(return_model)
    def put(self, id):
        borrow_api.payload["id"] = id
        borrow = borrowcollection.find_one({"id": id})
        if None is borrow:
            return Response(
                json.dumps({"error": "Borrow id not found"}),
                status=404,
                mimetype="application/json",
            )
        if "return_date" in borrow:
            return Response(
                json.dumps({"error": "Book already returned"}),
                status=404,
                mimetype="application/json",
            )
        del borrow["_id"]
        bookcollection.update_one(
            {"isbn": borrow["isbn"]}, {"$inc": {"nr_available": 1}}
        )
        borrowcollection.update_one(
            {"id": borrow_api.payload["id"]},
            {
                "$set": {
                    "return_date": dateutil.parser.parse(
                        borrow_api.payload["return_date"]
                    )
                }
            },
        )
        return Response(
            json.dumps(borrow_api.payload, default=str),
            status=200,
            mimetype="application/json",
        )


@borrow_api.route("/<string:id>")
class Borrow(Resource):
    def get(self, id):
        borrow = borrowcollection.find_one({"id": id})
        if None is borrow:
            return Response(
                json.dumps({"error": "Borrow id not found"}),
                status=404,
                mimetype="application/json",
            )
        del borrow["_id"]
        user = get_user(borrow["userid"])
        borrow["user_name"] = user.name
        borrow["user_email"] = user.email
        book = bookcollection.find_one({"isbn": borrow["isbn"]})
        if None is book:
            return Response(
                json.dumps({"error": "Book not found"}),
                status=404,
                mimetype="application/json",
            )
        borrow["book_name"] = book["name"]
        borrow["book_author"] = book["author"]
        return Response(
            json.dumps(borrow, default=str), status=200, mimetype="application/json"
        )

    @borrow_api.doc(responses={200: "Ok"})
    @borrow_api.expect(borrow_model)
    def put(self, id):
        session = mongo_client.start_session()
        session.start_transaction()
        try:
            borrow = borrowcollection.find_one({"id": id}, session=session)
            if None is not borrow:
                return Response(
                    json.dumps({"error": "Borrow already used"}),
                    status=404,
                    mimetype="application/json",
                )
            borrow_api.payload["id"] = id
            user = get_user(borrow_api.payload["userid"])
            if not user.exists:
                return Response(
                    json.dumps({"error": "User not found"}),
                    status=404,
                    mimetype="application/json",
                )
            book = bookcollection.find_one(
                {"isbn": borrow_api.payload["isbn"]}, session=session
            )
            if book is None:
                return Response(
                    json.dumps({"error": "Book not found"}),
                    status=404,
                    mimetype="application/json",
                )
            if book["nr_available"] < 1:
                return Response(
                    json.dumps({"error": "Book is not available yet"}),
                    status=404,
                    mimetype="application/json",
                )
            borrow_api.payload["borrow_date"] = dateutil.parser.parse(
                borrow_api.payload["borrow_date"]
            )
            borrow_api.payload["max_return_date"] = dateutil.parser.parse(
                borrow_api.payload["max_return_date"]
            )
            borrow_api.payload.pop("return_date", None)
            borrowcollection.insert_one(borrow_api.payload, session=session)
            bookcollection.update_one(
                {"isbn": borrow_api.payload["isbn"]},
                {"$inc": {"nr_available": -1}},
                session=session,
            )
            del borrow_api.payload["_id"]
            db_entry = borrowcollection.find_one({"id": id}, session=session)
            session.commit_transaction()
        except Exception as e:
            session.end_session()
            return Response(
                json.dumps({"error": str(e)}, default=str),
                status=500,
                mimetype="application/json",
            )

        session.end_session()
        return Response(
            json.dumps(db_entry, default=str), status=200, mimetype="application/json"
        )


@borrow_api.route("")
class BorrowList(Resource):
    @borrow_api.marshal_with(borrow_model, as_list=True)
    @borrow_api.expect(pagination_parser, validate=True)
    def get(self):
        args = pagination_parser.parse_args(request)
        data = (
            borrowcollection.find()
            .sort("id", 1)
            .limit(args["limit"])
            .skip(args["offset"])
        )
        extracted = [
            {
                "id": d["id"],
                "userid": d["userid"],
                "isbn": d["isbn"],
                "borrow_date": d["borrow_date"],
                "return_date": d["return_date"] if "return_date" in d else None,
                "max_return_date": d["max_return_date"],
            }
            for d in data
        ]
        return extracted


@book_api.route("/<string:isbn>")
class Book(Resource):
    def get(self, isbn):
        book = bookcollection.find_one({"isbn": isbn})
        if None is book:
            return Response(
                json.dumps({"error": "Book not found"}),
                status=404,
                mimetype="application/json",
            )
        del book["_id"]
        return Response(json.dumps(book), status=200, mimetype="application/json")

    @book_api.doc(responses={200: "Ok"})
    @book_api.expect(book_model)
    def put(self, isbn):
        book_api.payload["isbn"] = isbn
        try:
            bookcollection.insert_one(book_api.payload)
        except errors.DuplicateKeyError:
            return Response(
                json.dumps({"error": "Isbn already exists"}),
                status=404,
                mimetype="application/json",
            )
        del book_api.payload["_id"]
        return Response(
            json.dumps(book_api.payload), status=200, mimetype="application/json"
        )

    def delete(self, isbn):
        bookcollection.delete_one({"isbn": isbn})
        return Response("", status=200, mimetype="application/json")


@book_api.route("")
class BookList(Resource):
    @book_api.marshal_with(book_model, as_list=True)
    @book_api.expect(pagination_parser, validate=True)
    def get(self):
        args = pagination_parser.parse_args(request)
        books = (
            bookcollection.find()
            .sort("id", 1)
            .limit(args["limit"])
            .skip(args["offset"])
        )
        extracted = [
            {
                "isbn": d["isbn"],
                "name": d["name"],
                "author": d["author"],
                "publisher": d["publisher"],
                "nr_available": d["nr_available"],
            }
            for d in books
        ]
        return extracted


if __name__ == "__main__":
    try:
        mongo_client.admin.command("replSetInitiate")
    except errors.OperationFailure as e:
        logger.error("Error setting mongodb replSetInitiate error: {0}".format(str(e)))
    bookcollection.insert_one({"isbn": 0})
    bookcollection.delete_one({"isbn": 0})
    borrowcollection.insert_one({"id": 0})
    borrowcollection.delete_one({"id": 0})

    bookcollection.create_index("isbn", unique=True)
    # starts the app in debug mode, bind on all ip's and on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
