"""
Bank Reconciliation Service

Service for comparing bank statements with application transactions.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
import difflib

from app.models.reconciliation import BankReconciliation, ReconciliationMatch
from app.models.transaction import Transaction
from app.models.account import Account


class ReconciliationService:
    def __init__(self, db: Session):
        self.db = db

    def create_reconciliation(
        self,
        account_id: int,
        period_start: datetime,
        period_end: datetime,
        bank_transactions: List[Dict[str, Any]],
        bank_balance: Optional[Decimal] = None
    ) -> BankReconciliation:
        """
        Create a new bank reconciliation session

        Args:
            account_id: ID of the account to reconcile
            period_start: Start of reconciliation period
            period_end: End of reconciliation period
            bank_transactions: List of bank transactions from CSV
            bank_balance: Final balance from bank statement

        Returns:
            BankReconciliation object
        """
        # Get app transactions for the same period
        app_transactions = self.db.query(Transaction).filter(
            Transaction.account_id == account_id,
            Transaction.date >= period_start,
            Transaction.date <= period_end
        ).all()

        # Calculate app balance
        account = self.db.query(Account).filter(Account.id == account_id).first()
        app_balance = account.balance if account else Decimal('0')

        # Create reconciliation
        reconciliation = BankReconciliation(
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            bank_balance=bank_balance,
            app_balance=app_balance,
            difference=bank_balance - app_balance if bank_balance else None,
            status="pending",
            total_bank_transactions=len(bank_transactions)
        )
        self.db.add(reconciliation)
        self.db.flush()

        # Match transactions
        matches = self._match_transactions(
            reconciliation_id=reconciliation.id,
            bank_transactions=bank_transactions,
            app_transactions=app_transactions
        )

        # Add matches to database
        for match in matches:
            self.db.add(match)

        # Update statistics
        reconciliation.matched_count = sum(1 for m in matches if m.match_status == "matched")
        reconciliation.unmatched_bank_count = sum(1 for m in matches if m.match_status == "unmatched_bank")
        reconciliation.unmatched_app_count = sum(1 for m in matches if m.match_status == "unmatched_app")

        self.db.commit()
        self.db.refresh(reconciliation)

        return reconciliation

    def _match_transactions(
        self,
        reconciliation_id: int,
        bank_transactions: List[Dict[str, Any]],
        app_transactions: List[Transaction]
    ) -> List[ReconciliationMatch]:
        """
        Match bank transactions with app transactions

        Returns:
            List of ReconciliationMatch objects
        """
        matches = []
        used_app_transactions = set()

        # Try to match each bank transaction
        for bank_tx in bank_transactions:
            bank_date = bank_tx['date']
            bank_amount = Decimal(str(bank_tx['amount']))
            bank_description = bank_tx.get('description', '')

            # Find best match
            best_match = None
            best_confidence = 0

            for app_tx in app_transactions:
                if app_tx.id in used_app_transactions:
                    continue

                match_result = self._calculate_match_confidence(
                    bank_date=bank_date,
                    bank_amount=bank_amount,
                    bank_description=bank_description,
                    app_tx=app_tx
                )

                if match_result['confidence'] > best_confidence:
                    best_confidence = match_result['confidence']
                    best_match = (app_tx, match_result['type'])

            # Create match record
            if best_match and best_confidence >= 70:  # 70% threshold for automatic suggestion
                app_tx, match_type = best_match
                used_app_transactions.add(app_tx.id)

                match = ReconciliationMatch(
                    reconciliation_id=reconciliation_id,
                    transaction_id=app_tx.id,
                    bank_date=bank_date,
                    bank_amount=bank_amount,
                    bank_description=bank_description,
                    bank_reference=bank_tx.get('reference', ''),
                    match_status="matched",
                    match_confidence=best_confidence,
                    match_type=match_type
                )
            else:
                # Unmatched bank transaction
                match = ReconciliationMatch(
                    reconciliation_id=reconciliation_id,
                    transaction_id=None,
                    bank_date=bank_date,
                    bank_amount=bank_amount,
                    bank_description=bank_description,
                    bank_reference=bank_tx.get('reference', ''),
                    match_status="unmatched_bank",
                    match_confidence=0,
                    match_type=None
                )

            matches.append(match)

        # Add unmatched app transactions
        for app_tx in app_transactions:
            if app_tx.id not in used_app_transactions:
                match = ReconciliationMatch(
                    reconciliation_id=reconciliation_id,
                    transaction_id=app_tx.id,
                    bank_date=app_tx.date,
                    bank_amount=Decimal(str(app_tx.amount)),
                    bank_description="",
                    match_status="unmatched_app",
                    match_confidence=0,
                    match_type=None
                )
                matches.append(match)

        return matches

    def _calculate_match_confidence(
        self,
        bank_date: datetime,
        bank_amount: Decimal,
        bank_description: str,
        app_tx: Transaction
    ) -> Dict[str, Any]:
        """
        Calculate match confidence between bank transaction and app transaction

        Returns:
            Dict with 'confidence' (0-100) and 'type' (exact, fuzzy, date_amount)
        """
        confidence = 0
        match_type = "fuzzy"

        app_amount = Decimal(str(app_tx.amount))
        app_date = app_tx.date
        app_description = app_tx.description or ""

        # Check amount match (required)
        if abs(bank_amount - app_amount) > Decimal('0.01'):
            return {'confidence': 0, 'type': None}

        confidence += 50  # Amount matches

        # Check date match
        date_diff = abs((bank_date - app_date).days)
        if date_diff == 0:
            confidence += 30  # Exact date match
            match_type = "exact"
        elif date_diff <= 2:
            confidence += 15  # Within 2 days
        elif date_diff <= 5:
            confidence += 5  # Within 5 days

        # Check description similarity
        if bank_description and app_description:
            similarity = difflib.SequenceMatcher(
                None,
                bank_description.lower(),
                app_description.lower()
            ).ratio()

            confidence += int(similarity * 20)  # Up to 20 points for description

        # Exact match bonus
        if date_diff == 0 and similarity > 0.8:
            match_type = "exact"
            confidence = min(100, confidence + 10)

        return {
            'confidence': min(100, confidence),
            'type': match_type
        }

    def resolve_match(
        self,
        match_id: int,
        action: str,
        transaction_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> ReconciliationMatch:
        """
        Resolve a reconciliation match with user action

        Args:
            match_id: ID of the match to resolve
            action: Action to take (accept, ignore, create_transaction, link_existing)
            transaction_data: Data for creating new transaction (if action=create_transaction)
            notes: User notes

        Returns:
            Updated ReconciliationMatch
        """
        match = self.db.query(ReconciliationMatch).filter(
            ReconciliationMatch.id == match_id
        ).first()

        if not match:
            raise ValueError(f"Match {match_id} not found")

        # Handle action
        if action == "create_transaction":
            if not transaction_data:
                raise ValueError("transaction_data required for create_transaction action")

            # Get reconciliation to get account_id
            reconciliation = self.db.query(BankReconciliation).filter(
                BankReconciliation.id == match.reconciliation_id
            ).first()

            # Create new transaction
            new_tx = Transaction(
                account_id=reconciliation.account_id,
                date=match.bank_date,
                amount=float(match.bank_amount),
                description=transaction_data.get('description', match.bank_description),
                category=transaction_data.get('category'),
                notes=transaction_data.get('notes')
            )
            self.db.add(new_tx)
            self.db.flush()

            # Link match to new transaction
            match.transaction_id = new_tx.id
            match.match_status = "matched"
            match.match_type = "manual"

        elif action == "link_existing":
            if not transaction_data or 'transaction_id' not in transaction_data:
                raise ValueError("transaction_id required for link_existing action")

            match.transaction_id = transaction_data['transaction_id']
            match.match_status = "matched"
            match.match_type = "manual"

        elif action == "ignore":
            match.match_status = "unmatched_bank"

        elif action == "accept":
            # Accept suggested match
            if match.match_status != "matched":
                raise ValueError("Can only accept matched transactions")

        # Update match
        match.action = action
        match.action_taken_at = datetime.utcnow()
        match.user_notes = notes

        self.db.commit()
        self.db.refresh(match)

        return match

    def complete_reconciliation(self, reconciliation_id: int) -> BankReconciliation:
        """Mark reconciliation as completed"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id
        ).first()

        if not reconciliation:
            raise ValueError(f"Reconciliation {reconciliation_id} not found")

        reconciliation.status = "completed"
        reconciliation.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(reconciliation)

        return reconciliation

    def get_reconciliation_with_matches(self, reconciliation_id: int) -> Dict[str, Any]:
        """Get reconciliation with all matches"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id
        ).first()

        if not reconciliation:
            raise ValueError(f"Reconciliation {reconciliation_id} not found")

        # Get matches with transaction details
        matches_data = []
        for match in reconciliation.matches:
            match_dict = {
                'id': match.id,
                'bank_date': match.bank_date.isoformat(),
                'bank_amount': float(match.bank_amount),
                'bank_description': match.bank_description,
                'bank_reference': match.bank_reference,
                'match_status': match.match_status,
                'match_confidence': match.match_confidence,
                'match_type': match.match_type,
                'action': match.action,
                'user_notes': match.user_notes,
                'transaction': None
            }

            if match.transaction:
                match_dict['transaction'] = {
                    'id': match.transaction.id,
                    'date': match.transaction.date.isoformat(),
                    'amount': float(match.transaction.amount),
                    'description': match.transaction.description,
                    'category': match.transaction.category
                }

            matches_data.append(match_dict)

        return {
            'id': reconciliation.id,
            'account_id': reconciliation.account_id,
            'period_start': reconciliation.period_start.isoformat(),
            'period_end': reconciliation.period_end.isoformat(),
            'bank_balance': float(reconciliation.bank_balance) if reconciliation.bank_balance else None,
            'app_balance': float(reconciliation.app_balance) if reconciliation.app_balance else None,
            'difference': float(reconciliation.difference) if reconciliation.difference else None,
            'status': reconciliation.status,
            'total_bank_transactions': reconciliation.total_bank_transactions,
            'matched_count': reconciliation.matched_count,
            'unmatched_bank_count': reconciliation.unmatched_bank_count,
            'unmatched_app_count': reconciliation.unmatched_app_count,
            'created_at': reconciliation.created_at.isoformat(),
            'completed_at': reconciliation.completed_at.isoformat() if reconciliation.completed_at else None,
            'matches': matches_data
        }
