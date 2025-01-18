from app import db
from app.models import BaseModel
from datetime import datetime


class Category(db.Model, BaseModel):
    """
    Category Model for organizing transactions
    """
    __tablename__ = 'categories'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.String(50), db.ForeignKey('categories.id'))
    icon = db.Column(db.String(50), default='tag')  # FontAwesome icon name
    color = db.Column(db.String(50), default='blue')  # Color code for charts
    is_active = db.Column(db.Boolean, default=True)
    is_budget_tracked = db.Column(db.Boolean, default=True)

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    subcategories = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side='Category.id'),
        lazy='dynamic'
    )
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')

    # Category icon options with their display names
    ICON_CHOICES = {
        'tag': 'Tag',
        'shopping-cart': 'Shopping',
        'home': 'Home',
        'car': 'Transport',
        'utensils': 'Food',
        'medkit': 'Healthcare',
        'graduation-cap': 'Education',
        'gamepad': 'Entertainment',
        'gift': 'Gift',
        'plane': 'Travel',
        'piggy-bank': 'Savings',
        'money-bill': 'Salary',
        'chart-line': 'Investment',
        'ellipsis-h': 'Other'
    }

    # Category color options with their display names and hex codes
    COLOR_CHOICES = {
        'blue': {'name': 'Blue', 'code': '#3498db'},
        'green': {'name': 'Green', 'code': '#2ecc71'},
        'red': {'name': 'Red', 'code': '#e74c3c'},
        'yellow': {'name': 'Yellow', 'code': '#f1c40f'},
        'purple': {'name': 'Purple', 'code': '#9b59b6'},
        'orange': {'name': 'Orange', 'code': '#e67e22'},
        'teal': {'name': 'Teal', 'code': '#1abc9c'},
        'pink': {'name': 'Pink', 'code': '#e84393'},
        'gray': {'name': 'Gray', 'code': '#95a5a6'}
    }

    def __init__(self, name, user_id, description=None, parent_id=None,
                 icon='tag', color='blue', is_active=True, is_budget_tracked=True):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.parent_id = parent_id
        self.icon = icon
        self.color = color
        self.is_active = is_active
        self.is_budget_tracked = is_budget_tracked

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        """Convert category to dictionary with additional properties"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'color': self.color,
            'color_code': self.COLOR_CHOICES[self.color]['code'],
            'is_active': self.is_active,
            'is_budget_tracked': self.is_budget_tracked,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'has_subcategories': self.subcategories.count() > 0
        }

    def get_subcategories(self):
        """Get all subcategories for this category"""
        return self.subcategories.all()

    def get_all_subcategories(self):
        """Get all subcategories recursively"""
        all_subcategories = []
        for subcategory in self.subcategories:
            all_subcategories.append(subcategory)
            all_subcategories.extend(subcategory.get_all_subcategories())
        return all_subcategories

    def get_all_transactions(self):
        """Get all transactions for this category including subcategories"""
        all_transactions = list(self.transactions)
        for subcategory in self.subcategories:
            all_transactions.extend(subcategory.get_all_transactions())
        return all_transactions

    def get_parent_chain(self):
        """Get list of parent categories up to root"""
        chain = []
        current = self.parent
        while current:
            chain.append(current)
            current = current.parent
        return chain[::-1]  # Reverse to get root first

    def get_full_name(self):
        """Get full category name including parent categories"""
        chain = self.get_parent_chain()
        chain.append(self)
        return ' › '.join(category.name for category in chain)

    @staticmethod
    def get_color_hex(color_name):
        """Get hex code for a color name"""
        return Category.COLOR_CHOICES.get(color_name, {}).get('code', '#95a5a6')
