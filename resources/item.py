import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from db import db
from models import ItemModel
from schemas import ItemSchema,ItemupdateSchema
from flask_jwt_extended import jwt_required,get_jwt

blp = Blueprint("Items",__name__,description="Operations on items")

@blp.route("/item/<string:id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self,id):
        item = ItemModel.query.get_or_404(id)
        return item

    @jwt_required(fresh=True)
    def delete(self,id):
        jwt =get_jwt()
        if not jwt.get("is_admin"):
            abort(401,message="Admin Privildeges needed")
        item = ItemModel.query.get_or_404(id)
        db.delete(item)
        db.commit()
        return {"message":"Item deleted"}
    
    @jwt_required()
    @blp.arguments(ItemupdateSchema)
    @blp.response(201,ItemSchema)
    def put(self,data,id): # make sure the argument after self in the body being injected by blp and then id getting passed by the url
        item = ItemModel.query.get(id)
        if item:
            item.name = data['name']
            item.price = data['price']
        else:
            item_id = id
            item = ItemModel(id=item_id,**data)
        db.session.add(item)
        db.session.commit()
        return item

@jwt_required()
@blp.route("/item")
class Itemlist(MethodView):
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,data):
        item = ItemModel(**data)
        try:
            db.session.add(item) #this add the items to a file
            db.session.commit() # this commits the file to the database.
        except IntegrityError:
            abort(400, message="A store with this name already exsists")
        except SQLAlchemyError:
            abort(500, message="An error come while insterting the item ")
        return item




