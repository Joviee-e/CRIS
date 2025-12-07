# backend/app/auth/routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models import User
from .utils import make_jwt, get_role_from_token_or_db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Limiter should be initialized in app factory; if not already, do it here.
limiter = Limiter(key_func=get_remote_address, default_limits=[])

# Apply per-route strict limits for login/register
REGISTER_LIMIT = "5 per hour"
LOGIN_LIMIT = "10 per hour"

@bp.route("/register", methods=["POST"])
@limiter.limit(REGISTER_LIMIT)
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    pwd_hash = generate_password_hash(password)
    user = User(email=email, password_hash=pwd_hash)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "user with that email already exists"}), 409

    access, refresh = make_jwt(user)
    return jsonify({"access_token": access, "refresh_token": refresh, "user": user.to_dict()}), 201

@bp.route("/login", methods=["POST"])
@limiter.limit(LOGIN_LIMIT)
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        # generic response to avoid leaking if email exists
        return jsonify({"msg": "invalid credentials"}), 401

    access, refresh = make_jwt(user)
    return jsonify({"access_token": access, "refresh_token": refresh, "user": user.to_dict()}), 200

@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"msg": "user not found"}), 404
    access, _ = make_jwt(user)
    return jsonify({"access_token": access}), 200

# Admin-only endpoints (role promotion/demotion)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # get role from token or fallback to DB
        claims = get_jwt()
        identity = get_jwt_identity()
        role = get_role_from_token_or_db(claims, identity)
        if role != "admin":
            return jsonify({"msg": "admin privileges required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/promote", methods=["POST"])
@admin_required
def promote():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    new_role = data.get("role", "admin").strip()
    if not user_id:
        return jsonify({"msg": "user_id required"}), 400
    if len(new_role) > 30:
        return jsonify({"msg": "role too long"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "user not found"}), 404
    old_role = user.role
    user.role = new_role
    db.session.commit()
    return jsonify({"msg": "role updated", "user_id": user.id, "old_role": old_role, "new_role": new_role}), 200

@admin_bp.route("/demote", methods=["POST"])
@admin_required
def demote():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    new_role = data.get("role", "user").strip()
    if not user_id:
        return jsonify({"msg": "user_id required"}), 400
    if len(new_role) > 30:
        return jsonify({"msg": "role too long"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "user not found"}), 404
    old_role = user.role
    user.role = new_role
    db.session.commit()
    return jsonify({"msg": "role updated", "user_id": user.id, "old_role": old_role, "new_role": new_role}), 200
