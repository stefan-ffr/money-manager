"""Add federation_peers table

Revision ID: 006_add_federation_peers
Revises: 005_add_user_preferences
Create Date: 2026-06-02 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_federation_peers'
down_revision = '005_add_user_preferences'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'federation_peers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('api_endpoint', sa.String(255), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('origin', sa.String(20), server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain', name='uq_federation_peers_domain'),
    )
    op.create_index('ix_federation_peers_id', 'federation_peers', ['id'])
    op.create_index('ix_federation_peers_domain', 'federation_peers', ['domain'])


def downgrade() -> None:
    op.drop_index('ix_federation_peers_domain', 'federation_peers')
    op.drop_index('ix_federation_peers_id', 'federation_peers')
    op.drop_table('federation_peers')
