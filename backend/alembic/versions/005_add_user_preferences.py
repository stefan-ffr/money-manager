"""Add user_preferences table

Revision ID: 005_add_user_preferences
Revises: 004_add_recurring_transactions
Create Date: 2026-06-02 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_user_preferences'
down_revision = '004_add_recurring_transactions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('default_account_id', sa.Integer(), nullable=True),
        sa.Column('default_currency', sa.String(3), server_default='CHF'),
        sa.Column('date_format', sa.String(20), server_default='DD.MM.YYYY'),
        sa.Column('language', sa.String(5), server_default='de'),
        sa.Column('theme', sa.String(10), server_default='light'),
        sa.Column('email_notifications', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_preferences_user_id'),
    )
    op.create_index('ix_user_preferences_id', 'user_preferences', ['id'])
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    op.drop_index('ix_user_preferences_id', 'user_preferences')
    op.drop_table('user_preferences')
