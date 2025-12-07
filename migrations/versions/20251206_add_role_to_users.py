# backend/migrations/versions/20251206_add_role_to_users.py
"""add role to users and ensure uuid string pk

Revision ID: 20251206_add_role_to_users
Revises: <previous_rev>
Create Date: 2025-12-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251206_add_role_to_users'
down_revision = '1f2684708466'
branch_labels = None
depends_on = None

def upgrade():
    # Example: if table already exists, add column. If not create table.
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=30), nullable=False, server_default='user'))
        # Ensure email indexed and unique exists; if not, create index
        # batch_op.create_index('ix_users_email', ['email'], unique=True)

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('role')
