import json

from flask import Flask, request, Response
from flask_restplus import Api, Resource, fields
from pymongo import MongoClient, errors


app = Flask(__name__)
api = Api(app=app)
bookcollection = MongoClient('localhost', 27017).demo.bookcollection

book_model = api.model('Book', {
    'name': fields.String(description='Name of the book', required=True),
    'author': fields.String(description='Book author', required=True),
    'publisher': fields.String(description='Book publisher', required=True),
    'nr_available': fields.Integer(min=0, description='Nr books available for lend', required=True),
})


@api.route("/book/<int:id>")
class Book(Resource):
    def get(self, id):
        book = bookcollection.find_one({'_id': id})
        if None == book:
            return Response("", status=404, mimetype='application/json')
        return Response(json.dumps(book), status=200, mimetype='application/json')

    @api.doc(responses={200: 'Ok'})
    @api.expect(book_model)
    def put(self, id):
        bookcollection.insert_one(api.payload)
        return Response('', status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)