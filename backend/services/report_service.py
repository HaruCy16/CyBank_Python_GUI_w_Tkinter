# backend/services/report_service.py
from backend.services.account_service import list_accounts
from backend.services.transaction_service import get_transactions
from backend.services.bank_integration_service import list_bank_accounts
from datetime import datetime

def generate_account_summary(user_id: str) -> dict:
    """
    Generate a comprehensive summary of all CyBank accounts for a user.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary containing:
        - cybank_accounts: list of accounts with details
        - total_cybank_balance: sum of all CyBank accounts
        - account_count: number of accounts
        - generated_at: timestamp of report generation
    """
    accounts = list_accounts(user_id)
    
    account_details = []
    total_balance = 0.0
    
    for account in accounts:
        txn_count = len(get_transactions(account.account_id))
        account_details.append({
            "account_id": account.account_id,
            "account_name": account.account_name,
            "balance": account.balance,
            "transaction_count": txn_count,
            "created_at": str(account.created_at)
        })
        total_balance += account.balance
    
    return {
        "cybank_accounts": account_details,
        "total_cybank_balance": total_balance,
        "account_count": len(accounts),
        "generated_at": datetime.utcnow().isoformat()
    }


def generate_transaction_report(user_id: str, account_id: str = None) -> dict:
    """
    Generate transaction report for a user (optionally filtered by account).
    
    Args:
        user_id: User's unique identifier
        account_id: Optional - filter to specific account only
    
    Returns:
        Dictionary containing:
        - transactions: list of transaction details
        - total_credits: sum of all credit transactions
        - total_debits: sum of all debit transactions
        - net_change: total_credits - total_debits
        - transaction_count: total transactions
        - generated_at: timestamp
    """
    accounts = list_accounts(user_id)
    
    # Filter accounts if account_id specified
    if account_id:
        accounts = [a for a in accounts if a.account_id == account_id]
        if not accounts:
            return {"error": "Account not found", "transactions": []}
    
    transactions = []
    total_credits = 0.0
    total_debits = 0.0
    
    for account in accounts:
        account_txns = get_transactions(account.account_id)
        for txn in account_txns:
            transaction_details = {
                "transaction_id": txn.transaction_id,
                "account_id": txn.account_id,
                "account_name": account.account_name,
                "amount": txn.amount,
                "transaction_type": txn.transaction_type,
                "description": txn.description,
                "category": txn.category,
                "timestamp": str(txn.timestamp)
            }
            transactions.append(transaction_details)
            
            if txn.transaction_type == "CREDIT":
                total_credits += abs(txn.amount)
            else:
                total_debits += abs(txn.amount)
    
    # Sort by timestamp (newest first)
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "transactions": transactions,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_change": total_credits - total_debits,
        "transaction_count": len(transactions),
        "generated_at": datetime.utcnow().isoformat()
    }


def generate_multi_bank_portfolio(user_id: str) -> dict:
    """
    Generate a comprehensive portfolio analysis of all linked external banks.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary containing:
        - linked_banks: list of linked banks with details
        - bank_summary: breakdown by bank
        - total_linked_balance: sum across all linked banks
        - average_balance_per_bank: mean balance
        - bank_count: number of linked banks
        - generated_at: timestamp
    """
    banks = list_bank_accounts(user_id)
    
    bank_details = []
    total_balance = 0.0
    bank_by_type = {}
    
    for bank in banks:
        bank_info = {
            "linked_bank_id": bank.linked_bank_id,
            "bank_name": bank.bank_name,
            "account_number": bank.account_number,
            "account_type": bank.account_type,
            "balance": bank.balance,
            "last_synced": str(bank.last_synced)
        }
        bank_details.append(bank_info)
        total_balance += bank.balance
        
        # Group by account type
        if bank.account_type not in bank_by_type:
            bank_by_type[bank.account_type] = {
                "count": 0,
                "total_balance": 0.0,
                "banks": []
            }
        bank_by_type[bank.account_type]["count"] += 1
        bank_by_type[bank.account_type]["total_balance"] += bank.balance
        bank_by_type[bank.account_type]["banks"].append(bank.bank_name)
    
    average_balance = total_balance / len(banks) if banks else 0.0
    
    return {
        "linked_banks": bank_details,
        "bank_summary": bank_by_type,
        "total_linked_balance": total_balance,
        "average_balance_per_bank": average_balance,
        "bank_count": len(banks),
        "generated_at": datetime.utcnow().isoformat()
    }


def generate_complete_financial_report(user_id: str) -> dict:
    """
    Generate a complete financial report combining CyBank and linked bank data.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Dictionary containing all three reports plus combined analysis
    """
    cybank_summary = generate_account_summary(user_id)
    transaction_report = generate_transaction_report(user_id)
    portfolio_report = generate_multi_bank_portfolio(user_id)
    
    total_balance_all = cybank_summary["total_cybank_balance"] + portfolio_report["total_linked_balance"]
    
    return {
        "cybank_summary": cybank_summary,
        "transaction_report": transaction_report,
        "portfolio_report": portfolio_report,
        "combined_analysis": {
            "total_cybank_balance": cybank_summary["total_cybank_balance"],
            "total_linked_balance": portfolio_report["total_linked_balance"],
            "total_balance_all": total_balance_all,
            "cybank_percentage": (cybank_summary["total_cybank_balance"] / total_balance_all * 100) if total_balance_all > 0 else 0,
            "linked_percentage": (portfolio_report["total_linked_balance"] / total_balance_all * 100) if total_balance_all > 0 else 0,
            "total_transactions": transaction_report["transaction_count"],
            "total_accounts": cybank_summary["account_count"],
            "total_linked_banks": portfolio_report["bank_count"],
            "generated_at": datetime.utcnow().isoformat()
        }
    }
