# app/utils.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User
from app.extensions import db as _db

def role_required(*allowed_roles):
    """
    Decorator to ensure the JWT contains a role in allowed_roles.
    If role is missing in token claims, fallback to querying the DB
    for the user's current role using the identity (user id).
    Usage: @role_required("admin", "verifier")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # ensure JWT present
            verify_jwt_in_request()
            claims = get_jwt() or {}
            role = claims.get("role")

            # fallback: if role missing, look up user in DB by identity
            if role is None:
                try:
                    user_id = get_jwt_identity()
                    if user_id:
                        user = User.query.get(user_id)
                        if user:
                            role = getattr(user, "role", None)
                except Exception:
                    # if anything goes wrong, role remains None
                    role = None

            if role not in allowed_roles:
                return jsonify({"msg": "forbidden - insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
