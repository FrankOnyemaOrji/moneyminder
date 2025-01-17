from app import db
from app.models import BaseModel
from datetime import datetime
from decimal import Decimal

from app.models.transaction import Transaction


class Budget(db.Model, BaseModel):
    """
    Budget Model for setting spending limits per category
    """
    __tablename__ = 'budgets'

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    notification_threshold = db.Column(db.Integer, default=80)  # Percentage

    # Foreign Keys
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.String(50), db.ForeignKey('categories.id'), nullable=False)

    def __init__(self, amount, category_id, user_id, start_date, end_date,
                 notification_threshold=80):
        self.amount = Decimal(str(amount))
        self.category_id = category_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.notification_threshold = notification_threshold

    def __repr__(self):
        return f'<Budget {self.category.name} {self.amount}>'

    def get_spent_amount(self):
        """Calculate how much has been spent in this budget period"""
        spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category_id == self.category_id,
            Transaction.date >= self.start_date,
            Transaction.date <= self.end_date,
            Transaction.transaction_type == 'expense'
        ).scalar() or 0
        return Decimal(str(spent))

    def get_remaining_amount(self):
        """Calculate remaining budget"""
        return self.amount - self.get_spent_amount()

    def get_spending_percentage(self):
        """Calculate what percentage of budget has been spent"""
        spent = self.get_spent_amount()
        if self.amount > 0:
            return (spent / self.amount) * 100
        return 0

    def is_exceeded(self):
        """Check if budget has been exceeded"""
        return self.get_spent_amount() > self.amount

    def should_notify(self):
        """Check if user should be notified based on threshold"""
        spending_percentage = self.get_spending_percentage()
        return spending_percentage >= self.notification_threshold

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'category_id': self.category_id,
            'notification_threshold': self.notification_threshold,
            'spent_amount': float(self.get_spent_amount()),
            'remaining_amount': float(self.get_remaining_amount()),
            'spending_percentage': float(self.get_spending_percentage()),
            'is_exceeded': self.is_exceeded(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_active_budgets(user_id, date=None):
        """Get all active budgets for a specific date"""
        if date is None:
            date = datetime.utcnow()
        return Budget.query.filter(
            Budget.user_id == user_id,
            Budget.start_date <= date,
            Budget.end_date >= date
        ).all()
