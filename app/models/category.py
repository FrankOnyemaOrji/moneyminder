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

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    subcategories = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side='Category.id'),
        lazy='dynamic'
    )
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')

    def __init__(self, name, user_id, description=None, parent_id=None):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.parent_id = parent_id

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_subcategories(self):
        """Get all subcategories for this category"""
        return self.subcategories.all()

    def get_all_transactions(self):
        """Get all transactions for this category including subcategories"""
        all_transactions = self.transactions.all()
        for subcategory in self.subcategories:
            all_transactions.extend(subcategory.get_all_transactions())
        return all_transactions
