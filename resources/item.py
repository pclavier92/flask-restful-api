from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_claims, 
    jwt_optional, 
    get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank"
    )
    parser.add_argument('name',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id"
    )

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'},404

    @jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'error': "An item with name {} already exists".format(name)}, 400
        data = Item.parser.parse_args()
        item = ItemModel(**data)
        try:
            item.save_to_db()
        except:
            return {'message': 'Error inserting item'}, 500
        return item.json(), 201

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(**data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        item.save_to_db()
        return item.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()
        return {'message': 'Item deleted'}
        
class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = ItemModel.get_all()
        # If logged in
        if user_id:
            return {'items': [i.json() for i in items ]}, 200
            # list(map(lambda i: i.json(), items))
        return {
            'items': [i.name for i in items],
            'message': 'More info if logged in'
        }, 200