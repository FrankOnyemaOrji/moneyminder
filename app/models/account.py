from app import db
from app.models import BaseModel
from decimal import Decimal


class Account(db.Model, BaseModel):
    __tablename__ = 'accounts'

    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # bank, cash, mobile_money
    currency = db.Column(db.String(3), nullable=False, default='USD')
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    description = db.Column(db.Text)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    # Relationships
    transactions = db.relationship('Transaction', back_populates='account', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Account {self.name}>'

    def update_balance(self, amount: Decimal, transaction_type: str):
        """
        Update account balance based on transaction type
        """
        if transaction_type.lower() == 'income':
            self.balance += amount
        elif transaction_type.lower() == 'expense':
            self.balance -= amount
        self.update()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'currency': self.currency,
            'balance': float(self.balance),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
