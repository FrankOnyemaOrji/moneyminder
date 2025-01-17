from app import db
import uuid


def generate_id():
    return str(uuid.uuid4())


class BaseModel:
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

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


# Import all models here to avoid circular imports
from .user import User
from .account import Account
from .category import Category
from .transaction import Transaction
from .budget import Budget

__all__ = ['User', 'Account', 'Category', 'Transaction', 'Budget', 'BaseModel']
