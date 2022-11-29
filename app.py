from flask import Flask, request
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_bcrypt import Bcrypt

from flask_cors import CORS

from flask_migrate import Migrate

app = Flask(__name__)


class Config:
    """
    class config contains configurable parameters of the project
    """
    DEBUG = True
    SECRET_KEY = 'super-secret'
    VERSION = "1.0.0"


class DevelopmentConfig(Config):
    """
    Development config contains configurable parameters for development environment.
    It inherits the base config class
    """
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"

    JWT_SECRET_KEY = 'super-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    HOST = '0.0.0.0',


config = {"dev": DevelopmentConfig,
          "prod": None}

app.config.from_object(config.get("dev"),)

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/register", methods=["POST"])
def reg_user():
    body = request.json
    return user_registration(body)


@app.route("/login", methods=["POST"])
def login_user():
    body = request.json
    return user_login(body)


@app.route("/protected", methods=["GET"])
@jwt_required()
def prot():
    return {
        "message": "This route is protected"
    }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64))
    role = db.Column(db.String(6))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))


class UserSchema(ma.Schema):
    user_name = fields.Str()
    role = fields.Str()
    email = fields.Email()
    password = fields.Str()


class UserMeta(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id",
                  "user_name",
                  "role",
                  "email",
                  "password")


def user_registration(body):
    user = User(
        user_name=body.get("user_name"),
        role=body.get("role"),
        email=body.get("email"),
        password=bcrypt.generate_password_hash(body.get("password"))
    )
    db.session.add(user)
    db.session.commit()
    return{
        "status": True,
        "message": "User Added Successfully"
    }


def user_login(body):
    access_token = None
    refresh_token = None
    user = User.query.filter(User.email == body.get("email")).first()
    if user:
        message = "User logged in Successfully" if bcrypt.check_password_hash(
            user.password, body.get("password")) else "Incorrect Password"
        access_token = create_access_token(
            identity=(user.user_name, user.role))
        refresh_token = create_refresh_token(
            identity=(user.user_name, user.role))
    else:
        message = "User not found please register"

    return {
        "status": True,
        "message": message,
        "access_token": access_token,
        "refresh_token": refresh_token
    }


if __name__ == "__main__":
    app.run(debug=True)
