from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict
from app.models.shared_account import SharedAccount, SharedAccountMember, SplitTransaction, SplitShare, Settlement


def calculate_balance(db: Session, shared_account_id: int) -> List[Dict]:
    """Calculate who owes whom in a shared account"""
    
    # Get all members
    members = db.query(SharedAccountMember).filter(
        SharedAccountMember.shared_account_id == shared_account_id
    ).all()
    
    # Initialize balance dict
    balance = {member.user_identifier: Decimal("0.00") for member in members}
    
    # Get all split transactions
    transactions = db.query(SplitTransaction).filter(
        SplitTransaction.shared_account_id == shared_account_id,
        SplitTransaction.status.in_(["confirmed", "pending"])
    ).all()
    
    for transaction in transactions:
        # Person who paid gets credit
        balance[transaction.paid_by] += transaction.total_amount
        
        # Get shares
        shares = db.query(SplitShare).filter(
            SplitShare.split_transaction_id == transaction.id
        ).all()
        
        for share in shares:
            # Each person who owes gets debit
            balance[share.user_identifier] -= share.share_amount
    
    # Convert to list format
    result = []
    for user, amount in balance.items():
        result.append({
            "user": user,
            "amount": float(amount),
            "status": "owes" if amount < 0 else "owed" if amount > 0 else "settled"
        })
    
    return sorted(result, key=lambda x: x["amount"], reverse=True)


def calculate_settlements(db: Session, shared_account_id: int) -> List[Dict]:
    """Calculate optimal settlements using greedy algorithm"""
    
    balance_list = calculate_balance(db, shared_account_id)
    
    # Separate into creditors and debtors
    creditors = [(item["user"], Decimal(str(item["amount"]))) 
                 for item in balance_list if item["amount"] > 0]
    debtors = [(item["user"], abs(Decimal(str(item["amount"])))) 
               for item in balance_list if item["amount"] < 0]
    
    settlements = []
    
    # Greedy algorithm to minimize number of transactions
    while creditors and debtors:
        creditor, credit = creditors[0]
        debtor, debt = debtors[0]
        
        # Amount to settle
        settle_amount = min(credit, debt)
        
        settlements.append({
            "from": debtor,
            "to": creditor,
            "amount": float(settle_amount)
        })
        
        # Update amounts
        credit -= settle_amount
        debt -= settle_amount
        
        # Remove if settled
        if credit == 0:
            creditors.pop(0)
        else:
            creditors[0] = (creditor, credit)
        
        if debt == 0:
            debtors.pop(0)
        else:
            debtors[0] = (debtor, debt)
    
    return settlements


async def create_and_distribute_split(db: Session, account: SharedAccount, transaction_data):
    """Create split transaction and notify members"""
    from app.models.transaction import Transaction
    
    # Create split transaction
    split_tx = SplitTransaction(
        shared_account_id=account.id,
        paid_by=transaction_data.paid_by,
        total_amount=transaction_data.total_amount,
        date=transaction_data.date,
        description=transaction_data.description,
        category=transaction_data.category,
        status="pending"
    )
    db.add(split_tx)
    db.flush()
    
    # Get members
    members = db.query(SharedAccountMember).filter(
        SharedAccountMember.shared_account_id == account.id
    ).all()
    
    # Calculate shares based on split_type
    if transaction_data.split_type == "equal":
        share_amount = transaction_data.total_amount / len(members)
        share_percentage = Decimal("100") / len(members)
    else:
        # TODO: Implement percentage and custom splits
        share_amount = transaction_data.total_amount / len(members)
        share_percentage = Decimal("100") / len(members)
    
    # Create shares for each member except payer
    for member in members:
        if member.user_identifier != transaction_data.paid_by:
            share = SplitShare(
                split_transaction_id=split_tx.id,
                user_identifier=member.user_identifier,
                share_amount=share_amount,
                share_percentage=share_percentage,
                status="pending"
            )
            db.add(share)
            
            # TODO: Send to other instances if federated
            if member.instance_url:
                # await send_split_to_instance(member, split_tx, share)
                pass
    
    db.commit()
    db.refresh(split_tx)
    
    return {
        "transaction_id": split_tx.id,
        "status": "created",
        "shares_created": len(members) - 1
    }
