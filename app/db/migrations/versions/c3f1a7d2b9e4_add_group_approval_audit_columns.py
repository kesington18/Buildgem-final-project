"""add telegram adder and approval audit columns to telegram_groups

Revision ID: c3f1a7d2b9e4
Revises: a26a3bc08d0d
Create Date: 2026-10-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c3f1a7d2b9e4'
down_revision: Union[str, Sequence[str], None] = 'a26a3bc08d0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('telegram_groups', sa.Column('telegram_added_by_id', sa.BigInteger(), nullable=True))
    op.add_column('telegram_groups', sa.Column('telegram_added_by_name', sa.String(), nullable=True))
    op.add_column('telegram_groups', sa.Column('approved_by', sa.UUID(), nullable=True))
    op.add_column('telegram_groups', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_telegram_groups_approved_by_users', 'telegram_groups', 'users', ['approved_by'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_telegram_groups_approved_by_users', 'telegram_groups', type_='foreignkey')
    op.drop_column('telegram_groups', 'approved_at')
    op.drop_column('telegram_groups', 'approved_by')
    op.drop_column('telegram_groups', 'telegram_added_by_name')
    op.drop_column('telegram_groups', 'telegram_added_by_id')
