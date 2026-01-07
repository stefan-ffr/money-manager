"""Add source and requires_confirmation to transactions

Revision ID: 001_add_transaction_security
Revises: 
Create Date: 2024-12-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_transaction_security'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source column
    op.add_column('transactions', 
        sa.Column('source', sa.String(20), server_default='manual', nullable=False)
    )
    
    # Add requires_confirmation column
    op.add_column('transactions',
        sa.Column('requires_confirmation', sa.Boolean(), server_default='false', nullable=False)
    )
    
    # Update existing transactions from telegram
    op.execute("""
        UPDATE transactions 
        SET source = 'telegram', requires_confirmation = true 
        WHERE telegram_message_id IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_column('transactions', 'requires_confirmation')
    op.drop_column('transactions', 'source')
