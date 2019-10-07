import json

from flask import Flask, request, Response
from flask_restplus import Api, Resource, fields, reqparse
from pymongo import MongoClient, errors


app = Flask(__name__)
api = Api(app=app)
bookcollection = MongoClient('localhost', 27017).demo.bookcollection

book_model = api.model('Book', {
    'isbn': fields.String(description='ISBN', required=True),
    'name': fields.String(description='Name of the book', required=True),
    'author': fields.String(description='Book author', required=True),
    'publisher': fields.String(description='Book publisher', required=True),
    'nr_available': fields.Integer(min=0, description='Nr books available for lend', required=True),
})


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
        bookcollection.insert_one(api.payload)
        return Response('', status=200, mimetype='application/json')

    def delete(self, isbn):
        bookcollection.delete_one({'isbn': isbn})
        return Response('', status=200, mimetype='application/json')


pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('limit', type=int, help='Limit')
pagination_parser.add_argument('offset', type=int, help='Offset')
pagination_parser.add_argument('name')

@api.route("/books")
class BookList(Resource):
    @api.marshal_with(book_model, as_list=True)
    @api.expect(pagination_parser, validate=True)
    def get(self):
        args = pagination_parser.parse_args(request)
        books = bookcollection.find().limit(args['limit']).skip(args['offset'])
        print(args)
        extracted = [
            {'isbn': d['isbn'],
             'name': d['name'],
             'author': d['author'],
             'publisher': d['publisher'],
             'nr_available': d['nr_available']
             } for d in books]
        return extracted


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)