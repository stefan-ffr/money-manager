"""Add api_keys table and transactions.external_ref

Revision ID: 007_add_api_keys_and_external_ref
Revises: 006_add_federation_peers
Create Date: 2026-06-02 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_add_api_keys_and_external_ref'
down_revision = '006_add_federation_peers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('key_prefix', sa.String(16), nullable=False),
        sa.Column('key_hash', sa.String(64), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash', name='uq_api_keys_key_hash'),
    )
    op.create_index('ix_api_keys_id', 'api_keys', ['id'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])

    op.add_column('transactions', sa.Column('external_ref', sa.String(128), nullable=True))
    op.create_index('ix_transactions_external_ref', 'transactions', ['external_ref'])


def downgrade() -> None:
    op.drop_index('ix_transactions_external_ref', 'transactions')
    op.drop_column('transactions', 'external_ref')
    op.drop_index('ix_api_keys_key_hash', 'api_keys')
    op.drop_index('ix_api_keys_user_id', 'api_keys')
    op.drop_index('ix_api_keys_id', 'api_keys')
    op.drop_table('api_keys')
