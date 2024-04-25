import flask
from flask import jsonify, request, make_response
from . import db_session
from .books import Book

blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/n', methods=['GET'])
def get_books():
    session = db_session.create_session()
    n = session.query(Book).all()
    return jsonify({'n': [book.to_dict() for book in n]})


@blueprint.route('/api/n/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    session = db_session.create_session()
    n = session.query(Book).get(book_id)
    return jsonify({'n': n.to_dict()})


@blueprint.route('/api/n', methods=['POST'])
def add_book():
    session = db_session.create_session()
    book = Book(author=request.json['author_id'], book=request.json['book'], genre1=request.json['genre1'], description=request.json['description'], mark=request.json['mark'], is_finished=request.json['is_finished'])
    session.add(book)
    session.commit()
    return jsonify({'fccess': 'OK'})
