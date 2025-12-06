# app/auth/__init__.py
"""
Auth package initializer.

Keep this file minimal. Do NOT create app.auth.extensions (that shadows
app.extensions). Import shared extension instances from the top-level
app.extensions module instead.
"""

# pull only the shared objects auth code might use
from app.extensions import db, jwt  # type: ignore

# optionally expose helpers / constants here if other modules import them
__all__ = ["db", "jwt"]
