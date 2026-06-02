"""Add recurring_transactions table

Revision ID: 004_add_recurring_transactions
Revises: 003_add_2fa_and_data_isolation
Create Date: 2026-06-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_recurring_transactions'
down_revision = '003_add_2fa_and_data_isolation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'recurring_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('interval', sa.String(20), nullable=False, server_default='monthly'),
        sa.Column('next_run', sa.Date(), nullable=False),
        sa.Column('last_run', sa.Date(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recurring_transactions_id', 'recurring_transactions', ['id'])
    op.create_index('ix_recurring_transactions_user_id', 'recurring_transactions', ['user_id'])
    op.create_index('ix_recurring_transactions_account_id', 'recurring_transactions', ['account_id'])
    op.create_index('ix_recurring_transactions_next_run', 'recurring_transactions', ['next_run'])


def downgrade() -> None:
    op.drop_index('ix_recurring_transactions_next_run', 'recurring_transactions')
    op.drop_index('ix_recurring_transactions_account_id', 'recurring_transactions')
    op.drop_index('ix_recurring_transactions_user_id', 'recurring_transactions')
    op.drop_index('ix_recurring_transactions_id', 'recurring_transactions')
    op.drop_table('recurring_transactions')
