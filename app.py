import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from resources.user import User, UserRegister, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.secret_key = 'some_secret_key' # app.config['JWT_SECRET_KEY']
# Could be sqlite, mysql, postgresql, oracle ... without changing any of the code
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db') # second argument default value
# Turns off Flask-SQLAlchemy tracking but no for SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Propagates internal errors to the user (not secure, but good for debugin)
app.config['PROPAGATE_EXCEPTIONS'] = True 
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app) # not creating /auth

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    # Insted of hard-coding, you should read from a config file or db
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'message': 'Unauthorized to access this resource',
        'error': 'unauthorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(error):
    return jsonify({
        'message': 'Nedd fresh token to access this resource',
        'error': 'needs_fresh_token'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(error):
    return jsonify({
        'message': 'You dont have permission any more',
        'error': 'revoked_token'
    }), 401

api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserRegister,'/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(ItemList,'/items')
api.add_resource(Item,'/item/<string:name>')
api.add_resource(StoreList,'/stores')
api.add_resource(Store,'/store/<string:name>')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=8080, debug=True)