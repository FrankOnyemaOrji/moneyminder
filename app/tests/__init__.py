"""
Test suite initialization.
This module provides common test data and utilities used across test modules.
"""
from decimal import Decimal
from datetime import datetime, timedelta

__version__ = '1.0.0'

# Test Data Constants
TEST_DATA = {
    'user': {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    },
    'account': {
        'name': 'Test Account',
        'account_type': 'bank',
        'currency': 'USD',
        'initial_balance': Decimal('1000.00'),
        'description': 'Test account for integration testing'
    },
    'transaction': {
        'amount': Decimal('100.00'),
        'transaction_type': 'income',
        'description': 'Test transaction',
        'category': 'Salary',
        'tag': 'Base Pay'
    },
    'budget': {
        'amount': Decimal('500.00'),
        'category': 'Food',
        'tag': 'Groceries',
        'duration_days': 30
    }
}

# Test Configuration
TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-secret-key'
}
