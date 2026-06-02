"""Service for generating due recurring transactions."""

import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction
from app.models.account import Account


def advance_date(d: date, interval: str) -> date:
    """Return the next occurrence date after ``d`` for the given interval."""
    if interval == "daily":
        return date.fromordinal(d.toordinal() + 1)
    if interval == "weekly":
        return date.fromordinal(d.toordinal() + 7)
    if interval == "yearly":
        # Handle Feb 29 -> Feb 28 on non-leap years
        try:
            return d.replace(year=d.year + 1)
        except ValueError:
            return d.replace(year=d.year + 1, day=28)
    # Default: monthly (clamp the day to the target month's length)
    month = d.month + 1
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))


def process_due_recurring(
    db: Session,
    as_of: Optional[date] = None,
    user_id: Optional[int] = None,
) -> int:
    """Create transactions for every active rule that is due on/before ``as_of``.

    Missed occurrences are caught up (a rule due several periods ago produces
    one transaction per missed period). Returns the number of transactions
    created.
    """
    if as_of is None:
        as_of = date.today()

    query = db.query(RecurringTransaction).filter(
        RecurringTransaction.active.is_(True),
        RecurringTransaction.next_run <= as_of,
    )
    if user_id is not None:
        query = query.filter(RecurringTransaction.user_id == user_id)

    created = 0
    for rule in query.all():
        account = db.query(Account).filter(Account.id == rule.account_id).first()
        if not account:
            continue

        # Catch up every occurrence that is due, guarding against runaway loops
        guard = 0
        while rule.next_run <= as_of and guard < 1000:
            guard += 1
            tx = Transaction(
                user_id=rule.user_id,
                account_id=rule.account_id,
                date=rule.next_run,
                amount=rule.amount,
                category=rule.category,
                description=rule.description,
                status="confirmed",
                source="recurring",
                requires_confirmation=False,
            )
            db.add(tx)
            account.balance = (account.balance or Decimal("0.00")) + rule.amount
            rule.last_run = rule.next_run
            rule.next_run = advance_date(rule.next_run, rule.interval)
            created += 1

    db.commit()
    return created
