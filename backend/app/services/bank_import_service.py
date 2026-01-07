"""
Bank Import Service - CSV Import mit Auto-Account-Matching
Unterstützt PostFinance, UBS, Raiffeisen, ZKB und weitere Schweizer Banken
"""

from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
import csv
import io
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction


class BankImportService:
    """Service für Bank CSV Imports mit automatischem Account Matching"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_bank_format(self, csv_content: str) -> Optional[str]:
        """Erkenne Bank-Format anhand CSV Header"""
        lines = csv_content.split('\n')
        if not lines:
            return None
        
        header = lines[0].lower()
        
        # PostFinance
        if 'buchungsdatum' in header and 'valuta' in header:
            return 'postfinance'
        
        # UBS
        if 'trade date' in header or 'handelsplatz' in header:
            return 'ubs'
        
        # Raiffeisen
        if 'avisierungstext' in header:
            return 'raiffeisen'
        
        # ZKB
        if 'wertstellung' in header and 'belastung' in header:
            return 'zkb'
        
        # Credit Suisse
        if 'booking date' in header and 'credit/debit' in header:
            return 'credit_suisse'
        
        return None
    
    def extract_account_identifier(self, csv_content: str, bank: str) -> Optional[str]:
        """Extrahiere IBAN/Account Number aus CSV"""
        lines = csv_content.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines
            # IBAN Pattern: CH + 2 digits + 5 alphanumeric + 12 digits
            if 'CH' in line:
                parts = line.split()
                for part in parts:
                    if part.startswith('CH') and len(part) == 21:
                        return part
            
            # Alternative: Account Number in header
            if 'konto' in line.lower() or 'account' in line.lower():
                # Extract number from line
                import re
                numbers = re.findall(r'\d{6,}', line)
                if numbers:
                    return numbers[0]
        
        return None
    
    def find_matching_account(self, bank_identifier: str) -> Optional[Account]:
        """Finde Account basierend auf Bank Identifier"""
        if not bank_identifier:
            return None
        
        # Exakte Match auf bank_identifier
        account = self.db.query(Account).filter(
            Account.bank_identifier == bank_identifier
        ).first()
        
        if account:
            return account
        
        # Fallback: Match auf IBAN field
        account = self.db.query(Account).filter(
            Account.iban == bank_identifier
        ).first()
        
        return account
    
    def parse_postfinance(self, csv_content: str) -> List[Dict]:
        """Parse PostFinance CSV Format"""
        transactions = []
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        
        for row in reader:
            try:
                # PostFinance Format:
                # Buchungsdatum;Valuta;Avisierungstext;Gutschrift;Lastschrift;Saldo
                date = datetime.strptime(row['Buchungsdatum'], '%d.%m.%Y').date()
                
                # Determine amount (Gutschrift or Lastschrift)
                amount = Decimal(row.get('Gutschrift', '0').replace("'", ""))
                if not amount:
                    amount = -Decimal(row.get('Lastschrift', '0').replace("'", ""))
                
                transactions.append({
                    'date': date,
                    'amount': amount,
                    'description': row['Avisierungstext'],
                    'balance': Decimal(row['Saldo'].replace("'", "")) if row.get('Saldo') else None
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue
        
        return transactions
    
    def parse_ubs(self, csv_content: str) -> List[Dict]:
        """Parse UBS CSV Format"""
        transactions = []
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=',')
        
        for row in reader:
            try:
                # UBS Format varies, common fields:
                date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                amount = Decimal(row['Amount'])
                
                transactions.append({
                    'date': date,
                    'amount': amount,
                    'description': row.get('Description', row.get('Text', '')),
                    'balance': Decimal(row['Balance']) if row.get('Balance') else None
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue
        
        return transactions
    
    def parse_raiffeisen(self, csv_content: str) -> List[Dict]:
        """Parse Raiffeisen CSV Format"""
        transactions = []
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        
        for row in reader:
            try:
                date = datetime.strptime(row['Buchung'], '%d.%m.%Y').date()
                
                # Raiffeisen hat separate Soll/Haben Spalten
                amount = Decimal(row.get('Haben', '0').replace("'", ""))
                if not amount:
                    amount = -Decimal(row.get('Soll', '0').replace("'", ""))
                
                transactions.append({
                    'date': date,
                    'amount': amount,
                    'description': row['Avisierungstext'],
                    'balance': None
                })
            except Exception as e:
                continue
        
        return transactions
    
    def parse_zkb(self, csv_content: str) -> List[Dict]:
        """Parse ZKB (Zürcher Kantonalbank) CSV Format"""
        transactions = []
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        
        for row in reader:
            try:
                date = datetime.strptime(row['Wertstellung'], '%d.%m.%Y').date()
                
                # ZKB: Belastung (negative) oder Gutschrift (positive)
                amount = Decimal(row.get('Gutschrift', '0').replace("'", ""))
                if not amount:
                    amount = -Decimal(row.get('Belastung', '0').replace("'", ""))
                
                transactions.append({
                    'date': date,
                    'amount': amount,
                    'description': row['Beschreibung'],
                    'balance': None
                })
            except Exception as e:
                continue
        
        return transactions
    
    def import_csv(
        self,
        csv_content: str,
        account_id: Optional[int] = None,
        auto_match: bool = True
    ) -> Dict:
        """
        Hauptfunktion: Importiere CSV
        
        Args:
            csv_content: CSV File Content
            account_id: Optional - spezifischer Account
            auto_match: Wenn True, versuche automatisch Account zu finden
        
        Returns:
            Dict mit import results
        """
        # Detect bank format
        bank = self.detect_bank_format(csv_content)
        if not bank:
            return {
                'success': False,
                'error': 'Unknown bank format',
                'supported_banks': ['postfinance', 'ubs', 'raiffeisen', 'zkb', 'credit_suisse']
            }
        
        # Auto-match account wenn nicht gegeben
        account = None
        if account_id:
            account = self.db.query(Account).filter(Account.id == account_id).first()
        elif auto_match:
            bank_identifier = self.extract_account_identifier(csv_content, bank)
            if bank_identifier:
                account = self.find_matching_account(bank_identifier)
        
        if not account:
            return {
                'success': False,
                'error': 'No matching account found',
                'bank_identifier': self.extract_account_identifier(csv_content, bank),
                'hint': 'Set bank_identifier on account or provide account_id'
            }
        
        # Parse transactions based on bank
        parser_map = {
            'postfinance': self.parse_postfinance,
            'ubs': self.parse_ubs,
            'raiffeisen': self.parse_raiffeisen,
            'zkb': self.parse_zkb,
        }
        
        parser = parser_map.get(bank)
        if not parser:
            return {
                'success': False,
                'error': f'Parser for {bank} not implemented yet'
            }
        
        parsed_transactions = parser(csv_content)
        
        # Create transactions with duplicate detection
        created = 0
        duplicates = 0
        
        for tx_data in parsed_transactions:
            # Check for duplicate (same date, amount, description)
            existing = self.db.query(Transaction).filter(
                Transaction.account_id == account.id,
                Transaction.date == tx_data['date'],
                Transaction.amount == tx_data['amount'],
                Transaction.description == tx_data['description']
            ).first()
            
            if existing:
                duplicates += 1
                continue
            
            # Create transaction
            transaction = Transaction(
                account_id=account.id,
                date=tx_data['date'],
                amount=tx_data['amount'],
                description=tx_data['description'],
                status='pending',
                source='csv_import',
                requires_confirmation=True  # CSV Imports müssen bestätigt werden!
            )
            
            self.db.add(transaction)
            created += 1
        
        self.db.commit()
        
        # Update account last_import_date
        account.last_import_date = datetime.utcnow()
        self.db.commit()
        
        return {
            'success': True,
            'bank': bank,
            'account_id': account.id,
            'account_name': account.name,
            'transactions_created': created,
            'duplicates_skipped': duplicates,
            'total_parsed': len(parsed_transactions)
        }


# Helper function für Account Setup
def setup_bank_account(
    db: Session,
    account_id: int,
    bank_name: str,
    bank_identifier: str,
    enable_auto_import: bool = True
) -> Account:
    """Konfiguriere Account für Bank Import"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError(f"Account {account_id} not found")
    
    account.bank_name = bank_name
    account.bank_identifier = bank_identifier
    account.bank_import_enabled = enable_auto_import
    
    db.commit()
    db.refresh(account)
    
    return account
