from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(80),unique=True,nullable=False)
    
    items = db.relationship("ItemModel",back_populates="store",lazy="dynamic",cascade="all,delete")
    # WHen we go for deletion of store the problem comes that item linked with cannot have store_id as null. We have defined it has non-nullable so we need to add cascade so that once the sote is deleted all the items assocaiated with it is also deleted.

    tags = db.relationship("TagModel",back_populates="store",lazy="dynamic")