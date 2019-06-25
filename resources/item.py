from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

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

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'},404

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

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()
        return {'message': 'Item deleted'}
        
class ItemList(Resource):
    def get(self):
        items = ItemModel.get_all()
        return {'items': [i.json() for i in items ]}
        # list(map(lambda i: i.json(), items))