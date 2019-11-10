import json
import requests

from flask import Flask, request, Response
from flask_restplus import Api, Resource, fields, reqparse
from pymongo import MongoClient, errors


app = Flask(__name__)
api = Api(app=app)

mongo_client = MongoClient('localhost', 27017)
bookcollection = mongo_client.demo.bookcollection
borrowcollection = mongo_client.demo.borrowcollection


book_model = api.model('Book', {
    'isbn': fields.String(description='ISBN', required=True),
    'name': fields.String(description='Name of the book', required=True),
    'author': fields.String(description='Book author', required=True),
    'publisher': fields.String(description='Book publisher', required=True),
    'nr_available': fields.Integer(min=0, description='Nr books available for lend', required=True),
})

borrow_model = api.model('Borrow', {
    'id': fields.String(min=0, description='Unique uuid for borrowing', required=True),
    'userid': fields.Integer(min=0, description='Userid of the borrower', required=True),
    'isbn': fields.String(description='ISBN', required=True),
    'borrow_date': fields.DateTime(required=True),
    'return_date': fields.DateTime(required=True),
})

class User:
    def __init__(self, exists: bool, userid: int, name: str, email: str) -> None:
        self.exists = exists
        self.userid = userid
        self.name = name
        self.email = email


pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('limit', type=int, help='Limit')
pagination_parser.add_argument('offset', type=int, help='Offset')


def get_user(id: int) -> User:
    response = requests.get(url="http://localhost:81/users/" + str(id))
    if response.status_code != 200:
        return User(False, id, None, None)
    try:
        result = response.json()
        return User(True, id, result['name'], result['email'])
    except:
        return User(False, id, None, None)


@api.route("/borrow/<string:id>")
class Borrow(Resource):
    def get(self, id):
        borrow = borrowcollection.find_one({'id': id})
        del borrow['_id']
        if None == borrow:
            return Response("", status=404, mimetype='application/json')
        user = get_user(borrow['userid'])
        borrow['user_name'] = user.name
        borrow['user_email'] = user.email
        book = bookcollection.find_one({'isbn': borrow['isbn']})
        if None == book:
            return Response("", status=404, mimetype='application/json')
        borrow['book_name'] = book['name']
        borrow['book_author'] = book['author']

        return Response(json.dumps(borrow), status=200, mimetype='application/json')

    @api.doc(responses={200: 'Ok'})
    @api.expect(borrow_model)
    def put(self, id):
        api.payload['id'] = id
        user = get_user(api.payload['userid'])
        if not user.exists:
            return Response('Userid not found', status=404, mimetype='application/json')
        book = bookcollection.find_one({'isbn': api.payload['isbn']})
        if book is None:
            return Response('ISBN not found', status=404, mimetype='application/json')
        if book['nr_available'] < 1:
            return Response('Book is not available anymore', status=404, mimetype='application/json')
        borrowcollection.insert_one(api.payload)
        bookcollection.update_one(
            {'isbn': api.payload['isbn']},
            {'$inc': {'nr_available': -1}}
        )
        del api.payload['_id']
        return Response(json.dumps(api.payload), status=200, mimetype='application/json')


@api.route("/borrows")
class BorrowList(Resource):
    @api.marshal_with(borrow_model, as_list=True)
    @api.expect(pagination_parser, validate=True)
    def get(self):
        args = pagination_parser.parse_args(request)
        books = borrowcollection.find().limit(args['limit']).skip(args['offset'])
        extracted = [
            {'id': d['id'],
             'userid': d['userid'],
             'isbn': d['isbn'],
             'borrow_date': d['borrow_date'],
             'return_date': d['return_date'],
             } for d in books]
        return extracted


@api.route("/book/<string:isbn>")
class Book(Resource):
    def get(self, isbn):
        book = bookcollection.find_one({'isbn': isbn})
        del book['_id']
        if None == book:
            return Response("", status=404, mimetype='application/json')
        return Response(json.dumps(book), status=200, mimetype='application/json')

    @api.doc(responses={200: 'Ok'})
    @api.expect(book_model)
    def put(self, isbn):
        api.payload['isbn'] = isbn
        try:
            bookcollection.insert_one(api.payload)
        except errors.DuplicateKeyError:
            return Response(json.dumps({'error': 'Isbn already exists'}), status=404, mimetype='application/json')
        del api.payload['_id']
        return Response(json.dumps(api.payload), status=200, mimetype='application/json')

    def delete(self, isbn):
        bookcollection.delete_one({'isbn': isbn})
        return Response('', status=200, mimetype='application/json')


@api.route("/books")
class BookList(Resource):
    @api.marshal_with(book_model, as_list=True)
    @api.expect(pagination_parser, validate=True)
    def get(self):
        args = pagination_parser.parse_args(request)
        books = bookcollection.find().limit(args['limit']).skip(args['offset'])
        extracted = [
            {'isbn': d['isbn'],
             'name': d['name'],
             'author': d['author'],
             'publisher': d['publisher'],
             'nr_available': d['nr_available']
             } for d in books]
        return extracted


if __name__ == "__main__":
    bookcollection.create_index('isbn', unique=True)
    app.run(debug=True, host='0.0.0.0', port=5000)