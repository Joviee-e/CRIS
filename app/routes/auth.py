# app/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from app.extensions import db
from app.models import User

from app.auth.utils import make_tokens, get_role_from_token_or_db

auth_bp = Blueprint("auth_bp", __name__)
admin_bp = Blueprint("admin_bp", __name__)

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json() or {}
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"msg": "user exists"}), 409

    hashed = generate_password_hash(password)
    user = User(email=email, password_hash=hashed)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("db error on register")
        return jsonify({"msg": "db error"}), 500

    tokens = make_tokens(user)
    return jsonify({"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"], "user": user.to_dict()}), 201


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "invalid credentials"}), 401

    tokens = make_tokens(user)
    return jsonify({"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"], "user": user.to_dict()}), 200


# REFRESH: accepts refresh token, returns new access token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    # fallback: ensure user exists and fetch role
    role = get_role_from_token_or_db(get_jwt(), identity)
    # create new access token including role claim
    access_token = create_access_token(identity=identity, additional_claims={"role": role})
    return jsonify({"access_token": access_token}), 200


# Admin endpoints for promote/demote
def role_required(required_role):
    """
    Simple decorator factory: check role in JWT claims, fallback to DB if missing.
    """
    from functools import wraps

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            identity = get_jwt_identity()
            role = get_role_from_token_or_db(claims, identity)
            if role != required_role:
                return jsonify({"msg": f"{required_role} required"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@admin_bp.route("/promote", methods=["POST"])
@role_required("admin")
def promote():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    new_role = data.get("role")
    if not user_id or not new_role:
        return jsonify({"msg": "user_id and role required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "user not found"}), 404

    old_role = user.role
    user.role = new_role
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("db error promoting user")
        return jsonify({"msg": "db error"}), 500

    return jsonify({"msg": "role updated", "new_role": new_role, "old_role": old_role, "user_id": user.id}), 200


@admin_bp.route("/demote", methods=["POST"])
@role_required("admin")
def demote():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    new_role = data.get("role")
    if not user_id or not new_role:
        return jsonify({"msg": "user_id and role required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "user not found"}), 404

    old_role = user.role
    user.role = new_role
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("db error demoting user")
        return jsonify({"msg": "db error"}), 500

    return jsonify({"msg": "role updated", "new_role": new_role, "old_role": old_role, "user_id": user.id}), 200
