# app/auth/utils.py
from typing import Any, Dict, Optional

from flask_jwt_extended import create_access_token, create_refresh_token


def make_tokens(user) -> Dict[str, str]:
    """
    Create access & refresh tokens embedding user's role.
    `user` can be a model instance with .id and .role attributes.
    """
    identity = str(user.id)
    additional = {"role": getattr(user, "role", "user")}
    access = create_access_token(identity=identity, additional_claims=additional)
    refresh = create_refresh_token(identity=identity, additional_claims=additional)
    return {"access_token": access, "refresh_token": refresh}


def get_role_from_token_or_db(claims: Dict[str, Any], identity: Optional[str]) -> str:
    """
    Read 'role' from JWT claims if present, otherwise fallback to DB lookup.
    Import User lazily here to avoid circular imports at module import time.
    """
    # 1) Try token claims first
    if isinstance(claims, dict):
        role = claims.get("role")
        if role:
            return role

    # 2) Fallback: lazy import to avoid circular dependency
    try:
        from app.models import User  # local import
    except Exception:
        return "user"

    if identity is None:
        return "user"

    user = User.query.get(identity)
    if user:
        return getattr(user, "role", "user")
    return "user"
