"""per-group keywords, group owner, claim codes

Revision ID: d4a8e5b1c7f2
Revises: c3f1a7d2b9e4
Create Date: 2026-10-06 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd4a8e5b1c7f2'
down_revision: Union[str, Sequence[str], None] = 'c3f1a7d2b9e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('telegram_groups', sa.Column('owner_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_telegram_groups_owner_users', 'telegram_groups', 'users', ['owner_id'], ['id'])
    op.create_index('ix_telegram_groups_owner_id', 'telegram_groups', ['owner_id'])

    op.create_table(
        'group_claim_codes',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_group_claim_codes_code', 'group_claim_codes', ['code'], unique=True)

    op.add_column('keywords', sa.Column('group_id', sa.UUID(), nullable=True))
    op.add_column('keywords', sa.Column('status', sa.String(), nullable=False, server_default='approved'))
    op.create_foreign_key('fk_keywords_group_telegram_groups', 'keywords', 'telegram_groups', ['group_id'], ['id'])
    op.create_index('ix_keywords_group_id', 'keywords', ['group_id'])

    # Existing global keywords: give every existing group its own copy, then retire the globals
    # (kept, not deleted, because old announcements still link to them).
    op.execute("""
        INSERT INTO keywords (id, term, category, is_active, group_id, status, created_by, created_at)
        SELECT DISTINCT ON (g.id, k.term)
               gen_random_uuid(), k.term, k.category, true, g.id, 'approved', k.created_by, now()
        FROM keywords k CROSS JOIN telegram_groups g
        WHERE k.group_id IS NULL AND k.is_active = true
        ORDER BY g.id, k.term, k.created_at
    """)
    op.execute("UPDATE keywords SET is_active = false WHERE group_id IS NULL")

    op.create_unique_constraint('uq_keyword_group_term', 'keywords', ['group_id', 'term'])


def downgrade() -> None:
    op.drop_constraint('uq_keyword_group_term', 'keywords', type_='unique')
    op.drop_index('ix_keywords_group_id', table_name='keywords')
    op.drop_constraint('fk_keywords_group_telegram_groups', 'keywords', type_='foreignkey')
    op.drop_column('keywords', 'status')
    op.drop_column('keywords', 'group_id')
    op.drop_index('ix_group_claim_codes_code', table_name='group_claim_codes')
    op.drop_table('group_claim_codes')
    op.drop_index('ix_telegram_groups_owner_id', table_name='telegram_groups')
    op.drop_constraint('fk_telegram_groups_owner_users', 'telegram_groups', type_='foreignkey')
    op.drop_column('telegram_groups', 'owner_id')
