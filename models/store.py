from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    
    # lazy='dynamic' prevents from creating objects for every item from db
    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def json(self):
        itemsJson = [item.json() for item in self.items.all()]
        return {'name': self.name, 'items': itemsJson}
    
    @classmethod
    def get_all(cls):
        return StoreModel.query.all()

    @classmethod
    def find_by_name(cls,name):
        return cls.query.filter_by(name=name).first()
    
    # Insert or Update from db
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    