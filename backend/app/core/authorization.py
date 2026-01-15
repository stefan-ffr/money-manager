"""Authorization middleware and helper functions for data isolation"""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.category import Category


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Requires admin privileges (is_superuser=True)

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if they are an admin

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_user_filter(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Returns filter dictionary for data isolation.
    Admins see all data, regular users see only their own data.

    Args:
        current_user: Current authenticated user

    Returns:
        Dictionary to be used in SQLAlchemy filter_by()
        Empty dict for admins (no filtering), {"user_id": user_id} for regular users
    """
    if current_user.is_superuser:
        return {}  # Admins see all data
    return {"user_id": current_user.id}


def verify_resource_access(resource_user_id: int, current_user: User = Depends(get_current_user)) -> None:
    """
    Verify that the current user has access to a resource.
    Admins can access all resources, regular users can only access their own.

    Args:
        resource_user_id: The user_id of the resource being accessed
        current_user: Current authenticated user

    Raises:
        HTTPException: If user doesn't have access to the resource
    """
    if not current_user.is_superuser and resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )


def verify_account_access(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Account:
    """
    Verify that the current user has access to a specific account and return it.

    Args:
        account_id: ID of the account to check
        db: Database session
        current_user: Current authenticated user

    Returns:
        The account if access is granted

    Raises:
        HTTPException: If account not found or access denied
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    verify_resource_access(account.user_id, current_user)
    return account


def verify_transaction_access(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    """
    Verify that the current user has access to a specific transaction and return it.

    Args:
        transaction_id: ID of the transaction to check
        db: Database session
        current_user: Current authenticated user

    Returns:
        The transaction if access is granted

    Raises:
        HTTPException: If transaction not found or access denied
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    verify_resource_access(transaction.user_id, current_user)
    return transaction


def verify_category_access(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Category:
    """
    Verify that the current user has access to a specific category and return it.
    System categories (user_id is NULL) are accessible to everyone.

    Args:
        category_id: ID of the category to check
        db: Database session
        current_user: Current authenticated user

    Returns:
        The category if access is granted

    Raises:
        HTTPException: If category not found or access denied
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # System categories (user_id is NULL) are accessible to everyone
    if category.user_id is None:
        return category

    verify_resource_access(category.user_id, current_user)
    return category
