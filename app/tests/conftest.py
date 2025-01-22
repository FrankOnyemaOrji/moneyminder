"""
Pytest configuration and fixtures.
This module provides fixtures for testing the application.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from . import TEST_DATA, TEST_CONFIG
from app import create_app, db
from app.models import User, Account, Transaction, Budget
from ..config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance."""
    app = create_app(TestingConfig)

    # Update app config with test settings
    app.config.update(TEST_CONFIG)

    return app

@pytest.fixture(autouse=True)
def ignore_sqlalchemy_warnings():
    import warnings
    from sqlalchemy import exc as sa_exc
    warnings.filterwarnings('ignore',
                          category=sa_exc.SAWarning)
    warnings.filterwarnings('ignore',
                          message='.*Query.get.*',
                          category=Warning)


@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture(scope='function')
def database(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_user(database):
    """Create a test user."""
    user = User()
    user.username = TEST_DATA['user']['username']
    user.email = TEST_DATA['user']['email']
    user.set_password(TEST_DATA['user']['password'])
    user.save()
    return user


@pytest.fixture(scope='function')
def test_account(database, test_user):
    """Create a test account."""
    account = Account()
    account.name = TEST_DATA['account']['name']
    account.account_type = TEST_DATA['account']['account_type']
    account.currency = TEST_DATA['account']['currency']
    account.balance = TEST_DATA['account']['initial_balance']
    account.description = TEST_DATA['account']['description']
    account.user_id = test_user.id
    account.save()
    return account


@pytest.fixture(scope='function')
def test_transaction(database, test_user, test_account):
    """Create a test transaction."""
    transaction = Transaction(
        amount=TEST_DATA['transaction']['amount'],
        transaction_type=TEST_DATA['transaction']['transaction_type'],
        description=TEST_DATA['transaction']['description'],
        date=datetime.utcnow(),
        category=TEST_DATA['transaction']['category'],
        tag=TEST_DATA['transaction']['tag'],
        user_id=test_user.id,
        account_id=test_account.id
    )
    transaction.save()
    return transaction


@pytest.fixture(scope='function')
def test_budget(database, test_user):
    """Create a test budget."""
    now = datetime.utcnow()
    budget = Budget(
        amount=TEST_DATA['budget']['amount'],
        category=TEST_DATA['budget']['category'],
        user_id=test_user.id,
        start_date=now,
        end_date=now + timedelta(days=TEST_DATA['budget']['duration_days']),
        tag=TEST_DATA['budget']['tag']
    )
    budget.save()
    return budget


@pytest.fixture(scope='function')
def auth_headers(test_user):
    """Generate authentication headers for test user."""
    # Note: Implement your actual authentication token generation here
    return {'Authorization': f'Bearer test-token-{test_user.id}'}


@pytest.fixture(scope='function')
def authenticated_client(client, auth_headers):
    """Create an authenticated test client."""

    def _request(*args, **kwargs):
        # Add auth headers to each request
        headers = kwargs.pop('headers', {})
        headers.update(auth_headers)
        kwargs['headers'] = headers
        return client.open(*args, **kwargs)

    # Monkey patch the client's methods with authenticated versions
    for method in ['get', 'post', 'put', 'delete', 'patch']:
        setattr(client, method, lambda *a, **kw: _request(*a, method=method.upper(), **kw))

    return client
