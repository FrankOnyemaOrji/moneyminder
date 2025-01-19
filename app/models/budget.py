from app import db
from app.models import BaseModel
from datetime import datetime
from decimal import Decimal
from app.models.category import Category
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

    # Store category name directly instead of foreign key
    category = db.Column(db.String(100), nullable=False)

    # Optional: Store tag for more granular budgeting
    tag = db.Column(db.String(100), nullable=True)

    # Foreign Keys
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, amount, category, user_id, start_date, end_date,
                 tag=None, notification_threshold=80):
        self.amount = Decimal(str(amount))
        self.category = category
        self.tag = tag
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.notification_threshold = notification_threshold

    def __repr__(self):
        base_repr = f'<Budget {self.category} {self.amount}'
        if self.tag:
            return f'{base_repr} - {self.tag}>'
        return f'{base_repr}>'

    def get_spent_amount(self):
        """Calculate how much has been spent in this budget period"""
        query = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category == self.category,
            Transaction.date >= self.start_date,
            Transaction.date <= self.end_date,
            Transaction.transaction_type == 'expense'
        )

        # Add tag filter if specified
        if self.tag:
            query = query.filter(Transaction.tag == self.tag)

        spent = query.scalar() or 0
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

    def get_category_details(self):
        """Get category color and icon"""
        return Category.get_category_details(self.category)

    def to_dict(self):
        category_details = self.get_category_details()
        return {
            'id': self.id,
            'amount': float(self.amount),
            'start_date': self.start_date.strftime('%Y-%m-%d'),  # Format date here
            'end_date': self.end_date.strftime('%Y-%m-%d'),  # Format date here
            'category': self.category,
            'category_icon': category_details['icon'],
            'category_color': category_details['color'],
            'tag': self.tag,
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

    @staticmethod
    def validate_budget_data(category, tag=None):
        """Validate category and tag data"""
        if not Category.validate_category(category):
            raise ValueError(f"Invalid category: {category}")

        if tag and not Category.validate_tag(category, tag):
            raise ValueError(f"Invalid tag '{tag}' for category '{category}'")

        return True

    @classmethod
    def create_budget(cls, user_id, amount, category, start_date, end_date,
                      tag=None, notification_threshold=80):
        """Create a new budget with validation"""
        cls.validate_budget_data(category, tag)

        budget = cls(
            amount=amount,
            category=category,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            notification_threshold=notification_threshold
        )

        db.session.add(budget)
        db.session.commit()
        return budget
