from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


def generate_id():
    return str(uuid.uuid4())


class BaseModel:
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def save(self):
        """Save the model to the database"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_all(cls):
        return cls.query.all()


# Directly import and re-export models
from .user import User
from .account import Account
from .category import Category
from .transaction import Transaction
from .budget import Budget

__all__ = ['BaseModel', 'db', 'User', 'Account', 'Category', 'Transaction', 'Budget']

