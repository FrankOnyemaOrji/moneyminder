from app.models import db, BaseModel
from datetime import datetime
from decimal import Decimal
from app.models.category import Category
import logging

logger = logging.getLogger(__name__)


class Budget(db.Model, BaseModel):
    """Budget Model for setting spending limits per category"""
    __tablename__ = 'budgets'

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    notification_threshold = db.Column(db.Integer, default=80)
    category = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, amount, category, user_id, start_date, end_date, tag=None, notification_threshold=80):
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
        from app.models.transaction import Transaction

        try:
            query = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.user_id == self.user_id,
                Transaction.category == self.category,
                Transaction.date >= self.start_date,
                Transaction.date <= self.end_date,
                Transaction.transaction_type == 'expense'
            )

            if self.tag:
                query = query.filter(Transaction.tag == self.tag)

            # Log query for debugging
            logger.debug(f"Budget query for {self.category}: {str(query)}")

            spent = query.scalar() or Decimal('0')
            return Decimal(str(spent))

        except Exception as e:
            logger.error(f"Error calculating spent amount for budget {self.id}: {str(e)}")
            return Decimal('0')

    def get_remaining_amount(self):
        """Calculate remaining budget"""
        spent = self.get_spent_amount()
        remaining = self.amount - spent
        return remaining

    def get_spending_percentage(self):
        """Calculate what percentage of budget has been spent"""
        if self.amount <= 0:
            return Decimal('0')

        spent = self.get_spent_amount()
        percentage = (spent / self.amount * 100)
        return percentage.quantize(Decimal('0.01'))

    def is_exceeded(self):
        """Check if budget has been exceeded"""
        return self.get_spent_amount() > self.amount

    def should_notify(self):
        """Check if user should be notified based on threshold"""
        percentage = self.get_spending_percentage()
        return percentage >= self.notification_threshold

    def get_category_details(self):
        """Get category color and icon"""
        return Category.get_category_details(self.category)

    def to_dict(self):
        """Convert budget to dictionary with calculated values"""
        try:
            category_details = self.get_category_details()
            spent = self.get_spent_amount()
            remaining = self.get_remaining_amount()
            percentage = self.get_spending_percentage()

            return {
                'id': self.id,
                'amount': float(self.amount),
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d'),
                'category': self.category,
                'category_icon': category_details['icon'],
                'category_color': category_details['color'],
                'tag': self.tag,
                'notification_threshold': self.notification_threshold,
                'spent_amount': float(spent),
                'remaining_amount': float(remaining),
                'spending_percentage': float(percentage),
                'is_exceeded': self.is_exceeded(),
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error converting budget {self.id} to dict: {str(e)}")
            raise

    @staticmethod
    def get_active_budgets(user_id, date=None):
        """Get all active budgets for a specific date"""
        if date is None:
            date = datetime.utcnow()

        try:
            budgets = Budget.query.filter(
                Budget.user_id == user_id,
                Budget.start_date <= date,
                Budget.end_date >= date
            ).all()

            return budgets

        except Exception as e:
            logger.error(f"Error fetching active budgets: {str(e)}")
            return []

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
