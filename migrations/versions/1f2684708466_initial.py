"""initial schema aligned with current models

Revision ID: 1f2684708466
Revises: 
Create Date: 2025-12-05 22:05:37.945410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f2684708466'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- users table ---
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)

    # --- applications table ---
    op.create_table(
        'applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('sr_no', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=255), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('emp_no', sa.String(length=100), nullable=False),
        sa.Column('emp_name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=255), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_applications_sr_no', 'applications', ['sr_no'], unique=False)
    op.create_index('ix_applications_created_by', 'applications', ['created_by'], unique=False)

    # --- action_logs table ---
    op.create_table(
        'action_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('actor_id', sa.String(length=36), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_action_logs_application_id', 'action_logs', ['application_id'], unique=False)

    # --- attachments table ---
    op.create_table(
        'attachments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_attachments_application_id', 'attachments', ['application_id'], unique=False)


def downgrade():
    # Drop in reverse order of creation
    op.drop_index('ix_attachments_application_id', table_name='attachments')
    op.drop_table('attachments')

    op.drop_index('ix_action_logs_application_id', table_name='action_logs')
    op.drop_table('action_logs')

    op.drop_index('ix_applications_created_by', table_name='applications')
    op.drop_index('ix_applications_sr_no', table_name='applications')
    op.drop_table('applications')

    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
