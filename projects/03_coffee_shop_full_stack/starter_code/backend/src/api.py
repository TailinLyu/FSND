import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()
# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks_short = [drink.short() for drink in drinks]
    return jsonify(
        {
            'success': True,
            "drinks": drinks_short
        }
    ), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    drinks_long = [drink.long() for drink in drinks]
    return jsonify(
        {
            'success': True,
            "drinks": drinks_long
        }
    ), 200


@app.route('/drinks', methods=['Post'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    title = body['title']
    recipe = json.dumps(body['recipe'])
    print(title, recipe)
    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
    except Exception:
        abort(422)
    return jsonify(
        {
            'success': True,
            'drinks': drink.long()
        }
    ), 200


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    body = request.get_json()
    title = recipe = None
    if 'title' in body:
        title = body['title']
    if 'recipe' in body:
        recipe = json.dumps(body['recipe'])
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:
        abort(404)
    if not (title is None):
        drink.title = title
    if not (recipe is None):
        drink.recipe = recipe
    drink.update()
    drink_result = []
    drink_result.append(drink.long())
    return jsonify({
        "success": True,
        "drinks": drink_result
    }), 200


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify(
        {
            'success': True,
            'delete': drink_id
        }
    ), 200

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
