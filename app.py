import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.secret_key = 'some_secret_key'
# Could be sqlite, mysql, postgresql, oracle ... without changing any of the code
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db') # second argument default value
# Turns off Flask-SQLAlchemy tracking but no for SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

api.add_resource(UserRegister,'/register')
api.add_resource(ItemList,'/items')
api.add_resource(Item,'/item/<string:name>')
api.add_resource(StoreList,'/stores')
api.add_resource(Store,'/store/<string:name>')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=8080, debug=True)