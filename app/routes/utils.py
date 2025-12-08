# app/auth/utils.py
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from typing import Any, Dict
from app.models import User

def make_tokens(user: User) -> Dict[str, str]:
    """
    Create access and refresh tokens embedding the user's role as an additional claim.
    """
    identity = user.id
    additional = {"role": user.role}
    access = create_access_token(identity=identity, additional_claims=additional)
    refresh = create_refresh_token(identity=identity, additional_claims=additional)
    return {"access_token": access, "refresh_token": refresh}

def get_role_from_token_or_db(claims: Dict[str, Any], identity: str) -> str:
    """
    Read 'role' from token claims if present, otherwise fallback to DB lookup.
    Returns role string (default 'user' if not found).
    """
    role = None
    if isinstance(claims, dict):
        role = claims.get("role")
    if role:
        return role
    # fallback DB
    user = User.query.get(identity)
    if user:
        return user.role
    return "user"
