"""Add 2FA and data isolation

Revision ID: 003_add_2fa_and_data_isolation
Revises: 002_add_bank_import_fields
Create Date: 2026-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_2fa_and_data_isolation'
down_revision = '002_add_bank_import_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add user_id columns to accounts, transactions, and categories
    # First, add columns as nullable to allow backfilling
    op.add_column('accounts',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )
    op.add_column('transactions',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )
    op.add_column('categories',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

    # 2. Add 2FA fields to users table
    op.add_column('users',
        sa.Column('totp_secret', sa.String(255), nullable=True)
    )
    op.add_column('users',
        sa.Column('totp_enabled', sa.Boolean(), server_default='false', nullable=False)
    )
    op.add_column('users',
        sa.Column('backup_codes_hash', sa.Text(), nullable=True)
    )
    op.add_column('users',
        sa.Column('require_2fa', sa.Boolean(), server_default='false', nullable=False)
    )
    op.add_column('users',
        sa.Column('totp_last_used_at', sa.DateTime(), nullable=True)
    )

    # 3. Backfill existing data with first admin user
    # Get the first superuser
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM users WHERE is_superuser = true ORDER BY id LIMIT 1"))
    first_admin_row = result.fetchone()

    if first_admin_row:
        first_admin_id = first_admin_row[0]

        # Assign all existing accounts to first admin
        conn.execute(
            sa.text("UPDATE accounts SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": first_admin_id}
        )

        # Assign all existing transactions to first admin
        # We'll derive it from the account's user_id
        conn.execute(
            sa.text("""
                UPDATE transactions t
                SET user_id = a.user_id
                FROM accounts a
                WHERE t.account_id = a.id AND t.user_id IS NULL
            """)
        )

        # Categories remain nullable for system categories

        # Set require_2fa for existing admins
        conn.execute(
            sa.text("UPDATE users SET require_2fa = true WHERE is_superuser = true")
        )

    # 4. Make user_id NOT NULL for accounts and transactions (after backfill)
    op.alter_column('accounts', 'user_id', nullable=False)
    op.alter_column('transactions', 'user_id', nullable=False)

    # 5. Add foreign key constraints
    op.create_foreign_key(
        'fk_accounts_user_id',
        'accounts',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_transactions_user_id',
        'transactions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_categories_user_id',
        'categories',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # 6. Create backup_codes table
    op.create_table(
        'backup_codes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(255), nullable=False),
        sa.Column('used', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # 7. Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # 8. Create indexes for performance
    op.create_index('ix_accounts_user_id', 'accounts', ['user_id'])
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_categories_user_id', 'categories', ['user_id'])
    op.create_index('ix_backup_codes_user_id', 'backup_codes', ['user_id'])
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_audit_log_created_at', 'audit_log')
    op.drop_index('ix_audit_log_user_id', 'audit_log')
    op.drop_index('ix_backup_codes_user_id', 'backup_codes')
    op.drop_index('ix_categories_user_id', 'categories')
    op.drop_index('ix_transactions_user_id', 'transactions')
    op.drop_index('ix_accounts_user_id', 'accounts')

    # Drop tables
    op.drop_table('audit_log')
    op.drop_table('backup_codes')

    # Drop foreign key constraints
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')
    op.drop_constraint('fk_transactions_user_id', 'transactions', type_='foreignkey')
    op.drop_constraint('fk_accounts_user_id', 'accounts', type_='foreignkey')

    # Drop user_id columns
    op.drop_column('categories', 'user_id')
    op.drop_column('transactions', 'user_id')
    op.drop_column('accounts', 'user_id')

    # Drop 2FA fields from users
    op.drop_column('users', 'totp_last_used_at')
    op.drop_column('users', 'require_2fa')
    op.drop_column('users', 'backup_codes_hash')
    op.drop_column('users', 'totp_enabled')
    op.drop_column('users', 'totp_secret')
