from flask import Blueprint, request
from ..extensions import db
from ..models import User
from flask_jwt_extended import create_access_token, create_refresh_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    pwd = data.get("password")
    if User.query.filter_by(email=email).first():
        return {"msg": "exists"}, 400
    u = User(email=email)
    u.set_password(pwd)
    db.session.add(u)
    db.session.commit()
    return {"msg": "created"}, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    pwd = data.get("password")

    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(pwd):
        return {"msg": "bad credentials"}, 401

    access = create_access_token(identity={"id": u.id, "role": u.role})
    refresh = create_refresh_token(identity={"id": u.id, "role": u.role})

    return {"access": access, "refresh": refresh}
