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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    drinks_short = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_short
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    drinks_long = [drink.long() for drink in drinks]

    result = {
        'success': True,
        'drinks': drinks_long
        }
    
    return jsonify(result)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    body = request.get_json()

    # abort if no drink info in body
    if not ('title' in body and 'recipe' in body):
        abort(422)

    # get drink info
    title = body.get('title')
    recipe = body.get('recipe')

    try:
        # add the new drink
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
        'success': True,
        'created': drink_id,
        'drinks': drinks.long()
        })
    
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):

    # get drink based on id
    drink = Drink.query.filter_by(Drink.id == drink_id).one_or_none()

    if drink is None:
        return json.dumps({
            'success': False,
            'error': 'Drink #' + id + ' not found to be edited',
            }), 404

    try:
        body = request.get_json()

        # get drink info
        title = body.get('title')
        recipe = body.get('recipe')
        
        #if there is a title
        if 'title' in body:
            drink.title = title

        #if there is a recipe
        if 'recipe' in body:
            drink.recipe = recipe

        drink.update()

        return jsonify({
            'success': True,
            'updated': drink_id,
            'drinks': drinks.long()
        })

    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')

def delete_drink(jwt, id):
    drink = Drink.query.filter_by(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
        'success': True,
        'deleted': drink_id,
        })
    
    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
