from flask.views import MethodView
from flask_smorest import abort,Blueprint
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from db import db
from models import UserModel
from schemas import UserSchema
from flask_jwt_extended import create_access_token,get_jwt,jwt_required,create_refresh_token,get_jwt_identity
from blocklist import BLOCKLIST

blp = Blueprint("Users",__name__,description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        user = UserModel(username=user_data["username"],
                         password= pbkdf2_sha256.hash(user_data["password"])
                         )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="User was not created due to internal server error")
        except IntegrityError:
            abort(409, message="User already exsits!")
        return {"message":"User has been created"}

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200,UserSchema)
    def get(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"User has been deleted"}

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        user = UserModel.query.filter(UserModel.username==user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"],user.password):
            access_token = create_access_token(str(user.id),fresh=True)
            refresh_token = create_refresh_token(str(user.id))
            return {"access_token":access_token,"refresh_token":refresh_token}
        abort(401,message="Invalid Credentials")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt().get("jti")
        BLOCKLIST.add(jti)
        return {"message":"logout"}
    
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)
        jti = get_jwt().get("jti")
        BLOCKLIST.add(jti)
        return {"access_token":new_token}
