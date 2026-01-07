"""Add bank import fields to accounts

Revision ID: 002_add_bank_import_fields
Revises: 001_add_transaction_security
Create Date: 2024-12-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_bank_import_fields'
down_revision = '001_add_transaction_security'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add bank import fields to accounts
    op.add_column('accounts', 
        sa.Column('bank_name', sa.String(100), nullable=True)
    )
    
    op.add_column('accounts',
        sa.Column('bank_identifier', sa.String(100), nullable=True)
    )
    
    op.add_column('accounts',
        sa.Column('bank_import_enabled', sa.Boolean(), server_default='false', nullable=False)
    )
    
    op.add_column('accounts',
        sa.Column('last_import_date', sa.DateTime(), nullable=True)
    )
    
    # Create index on bank_identifier for faster lookups
    op.create_index(
        'ix_accounts_bank_identifier',
        'accounts',
        ['bank_identifier']
    )


def downgrade() -> None:
    op.drop_index('ix_accounts_bank_identifier', 'accounts')
    op.drop_column('accounts', 'last_import_date')
    op.drop_column('accounts', 'bank_import_enabled')
    op.drop_column('accounts', 'bank_identifier')
    op.drop_column('accounts', 'bank_name')
