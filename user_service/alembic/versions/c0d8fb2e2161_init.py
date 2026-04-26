"""init

Revision ID: c0d8fb2e2161
Revises: 
Create Date: 2026-04-26 23:33:27.365287
"""
from alembic import op
import sqlalchemy as sa


revision = 'c0d8fb2e2161'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('login', sa.String(length=50), nullable=False),
    sa.Column('hashed_password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_login'), table_name='users')
    op.drop_table('users')
