import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from models import StoreModel
from db import db
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_jwt_extended import jwt_required

blp = Blueprint("Stores",__name__,description="Operation on Stores")

@blp.route("/store/<string:id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self,id):
        store = StoreModel.query.get_or_404(id)
        return store

    @jwt_required()
    def delete(self,id):
        store = StoreModel.query.get_or_404(id)
        db.delete(store)
        db.commit()
        return {"message":"store is deleted"}

@blp.route("/store")
class Storelist(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201,StoreSchema)
    def post(self,data):
        store=StoreModel(**data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400,message="A store with the name already exsits")
        except SQLAlchemyError:
            abort(500,message="An error occured creating the store")
        return store
    
