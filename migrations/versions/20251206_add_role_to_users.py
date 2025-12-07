# backend/migrations/versions/20251206_add_role_to_users.py
"""no-op: role is created in initial revision

Revision ID: 20251206_add_role_to_users
Revises: 1f2684708466
Create Date: 2025-12-06 00:00:00.000000

"""
from alembic import op  # noqa: F401  (kept for Alembic's sake)
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = '20251206_add_role_to_users'
down_revision = '1f2684708466'
branch_labels = None
depends_on = None


def upgrade():
    # No-op: the `role` column is already created in the initial migration.
    pass


def downgrade():
    # No-op: nothing to undo.
    pass
