from app import db
from app.models import BaseModel
from datetime import datetime
from decimal import Decimal


class Transaction(db.Model, BaseModel):
    """
    Transaction Model for tracking financial transactions
    """
    __tablename__ = 'transactions'

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.String(50), db.ForeignKey('categories.id'), nullable=False)

    def __init__(self, amount, transaction_type, account_id, category_id, user_id,
                 description=None, date=None):
        self.amount = Decimal(str(amount))
        self.transaction_type = transaction_type.lower()
        self.account_id = account_id
        self.category_id = category_id
        self.user_id = user_id
        self.description = description
        self.date = date if date else datetime.utcnow()

    def __repr__(self):
        return f'<Transaction {self.transaction_type} {self.amount}>'

    def save(self):
        """Save transaction and update account balance"""
        db.session.add(self)
        self.account.update_balance(self.amount, self.transaction_type)
        db.session.commit()

    def delete(self):
        """Delete transaction and update account balance"""
        # Reverse the transaction effect on balance
        reverse_type = 'expense' if self.transaction_type == 'income' else 'income'
        self.account.update_balance(self.amount, reverse_type)
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'description': self.description,
            'date': self.date.isoformat(),
            'account_id': self.account_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_by_date_range(user_id, start_date, end_date):
        """Get all transactions within a date range"""
        return Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.desc()).all()
