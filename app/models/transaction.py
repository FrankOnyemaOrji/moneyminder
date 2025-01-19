# In models/transaction.py
from app.models import db, BaseModel
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
    category = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(100), nullable=False)

    # Foreign Keys
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=False)

    # Relationships
    account = db.relationship('Account', back_populates='transactions')

    def __init__(self, amount, transaction_type, account_id, category, tag, user_id,
                 description=None, date=None):
        self.amount = Decimal(str(amount))
        self.transaction_type = transaction_type.lower()
        self.account_id = account_id
        self.category = category
        self.tag = tag
        self.user_id = user_id
        self.description = description
        self.date = date if date else datetime.utcnow()

    def save(self):
        """Save transaction and update account balance"""
        try:
            # First, ensure we have the account loaded
            if not self.account:
                from app.models.account import Account
                self.account = Account.query.get(self.account_id)
                if not self.account:
                    raise ValueError(f"Account with ID {self.account_id} not found")

            db.session.add(self)
            self.account.update_balance(self.amount, self.transaction_type)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete transaction and update account balance"""
        # Reverse the transaction effect on balance
        reverse_type = 'expense' if self.transaction_type == 'income' else 'income'
        self.account.update_balance(self.amount, reverse_type)
        db.session.delete(self)
        db.session.commit()

    def get_category_icon(self):
        """Get the FontAwesome icon for this transaction's category"""
        from app.models.category import Category
        return Category.PRESET_CATEGORIES.get(self.category, {}).get('icon', 'tag')

    def get_category_color(self):
        """Get the color code for this transaction's category"""
        from app.models.category import Category
        return Category.PRESET_CATEGORIES.get(self.category, {}).get('color', '#718096')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'description': self.description,
            'date': self.date.isoformat(),
            'category': self.category,
            'tag': self.tag,
            'account_id': self.account_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category_icon': self.get_category_icon(),
            'category_color': self.get_category_color()
        }

    @staticmethod
    def get_by_date_range(user_id, start_date, end_date):
        """Get all transactions within a date range"""
        return Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.desc()).all()

    @staticmethod
    def get_category_summary(user_id, start_date=None, end_date=None):
        """Get transaction summary by category"""
        query = Transaction.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.all()

        summary = {}
        for transaction in transactions:
            if transaction.category not in summary:
                summary[transaction.category] = {
                    'income': 0,
                    'expense': 0,
                    'color': transaction.get_category_color(),
                    'icon': transaction.get_category_icon(),
                    'tags': {}
                }

            # Update category totals
            summary[transaction.category][transaction.transaction_type] += float(transaction.amount)

            # Update tag totals
            if transaction.tag not in summary[transaction.category]['tags']:
                summary[transaction.category]['tags'][transaction.tag] = {
                    'income': 0,
                    'expense': 0
                }
            summary[transaction.category]['tags'][transaction.tag][transaction.transaction_type] += float(
                transaction.amount)

        return summary

    @staticmethod
    def get_tag_summary(user_id, category=None, start_date=None, end_date=None):
        """Get transaction summary by tags within a category"""
        query = Transaction.query.filter_by(user_id=user_id)

        if category:
            query = query.filter_by(category=category)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.all()

        summary = {}
        for transaction in transactions:
            if transaction.tag not in summary:
                summary[transaction.tag] = {
                    'income': 0,
                    'expense': 0,
                    'category': transaction.category
                }

            summary[transaction.tag][transaction.transaction_type] += float(transaction.amount)

        return summary
