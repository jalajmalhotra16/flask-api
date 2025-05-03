from flask_smorest import abort,Blueprint
from flask.views import MethodView
from db import db
from models import TagModel,StoreModel,ItemModel
from schemas import TagSchema,TagAndItemSchema
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Tags",__name__,description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def post(self,tag_data,store_id):
        """if TagModel.query.filter(TagModel.store_id==store_id, TagModel.name== tag_data["name"]).first():
            abort(400,message="A tag with that name already exsits in the store")
        We have added unique in the schema so this is not needed but if we did not want unique in the db we can use the logic here.
        """
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag



#tag and items

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(400,message="tag and item needs to be of same store.")

        print(item)
        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occurred while inserting the tag")
        return tag
    
    
    @blp.response(200, TagAndItemSchema)
    def delete(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        print(item,tag)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500 , message="An error occured while unlinking the tag from item")
        return {"message":"Item removed from tag","item":item,"tag":tag}



@blp.route("/tag/<string:tag_id>")
class tags(MethodView):
    @blp.response(200, TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202,description="Deletes a tag if no items is tagged with it")
    @blp.alt_response(404,description="Tag not found")
    @blp.alt_response(400,description="Returned if the tag is assigned to one or mroe items. In this case, the tag is not deleted")
    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag deleted"}
        abort(400,message="Could not delete tag. Make sure tag is not associated with any items, then try again")

