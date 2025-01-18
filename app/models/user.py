from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models import BaseModel


class User(UserMixin, db.Model, BaseModel):
    """User Model for storing user related details"""
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships - cascade ensures child records are deleted when user is deleted
    accounts = db.relationship('Account', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic',
                                   cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def get_transaction_categories(self):
        """Get unique categories from user's transactions"""
        return sorted(list(set(t.category for t in self.transactions)))

    def get_transactions_by_category(self, category):
        """Get all transactions for a specific category"""
        return self.transactions.filter_by(category=category).all()

    def get_category_stats(self):
        """Get statistics for all categories used by user"""
        stats = {}
        for transaction in self.transactions:
            if transaction.category not in stats:
                stats[transaction.category] = {
                    'income': 0,
                    'expense': 0,
                    'transaction_count': 0,
                    'color': transaction.get_category_color(),
                    'icon': transaction.get_category_icon()
                }

            stats[transaction.category][transaction.transaction_type] += float(transaction.amount)
            stats[transaction.category]['transaction_count'] += 1

        return stats

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def get_by_email(cls, email):
        """Get user by email address"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()
