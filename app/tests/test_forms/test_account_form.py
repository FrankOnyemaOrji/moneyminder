import pytest
from decimal import Decimal
from app.forms.account import AccountForm, AccountEditForm, AccountDeleteForm
from .. import TEST_DATA


@pytest.mark.usefixtures('app')
class TestAccountForm:
    """Test cases for AccountForm."""

    def test_valid_account_form(self, app):
        """Test form with valid data."""
        with app.test_request_context():
            form = AccountForm(
                name=TEST_DATA['account']['name'],
                account_type=TEST_DATA['account']['account_type'],
                currency=TEST_DATA['account']['currency'],
                initial_balance=TEST_DATA['account']['initial_balance'],
                description=TEST_DATA['account']['description']
            )
            assert form.validate()

    def test_required_fields(self, app):
        """Test required field validation."""
        with app.test_request_context():
            form = AccountForm()
            assert not form.validate()
            required_fields = ['name', 'account_type', 'currency', 'initial_balance']
            for field in required_fields:
                assert field in form.errors

    def test_name_length_validation(self, app):
        """Test account name length validation."""
        with app.test_request_context():
            # Test too short name
            form = AccountForm(name='A')
            assert not form.validate()
            assert 'name' in form.errors
            assert 'must be between 2 and 100 characters' in form.errors['name'][0]

            # Test too long name
            form = AccountForm(name='A' * 101)
            assert not form.validate()
            assert 'name' in form.errors
            assert 'must be between 2 and 100 characters' in form.errors['name'][0]

    def test_invalid_account_type(self, app):
        """Test account type validation."""
        with app.test_request_context():
            form = AccountForm(account_type='invalid_type')
            assert not form.validate()
            assert 'account_type' in form.errors
            assert 'Not a valid choice' in form.errors['account_type'][0]

    def test_invalid_currency(self, app):
        """Test currency validation."""
        with app.test_request_context():
            form = AccountForm(currency='INVALID')
            assert not form.validate()
            assert 'currency' in form.errors
            assert 'Not a valid choice' in form.errors['currency'][0]

    def test_negative_balance(self, app):
        """Test initial balance validation."""
        with app.test_request_context():
            form = AccountForm(initial_balance=Decimal('-100.00'))
            assert not form.validate()
            assert 'initial_balance' in form.errors


@pytest.mark.usefixtures('app')
class TestAccountEditForm:
    """Test cases for AccountEditForm."""

    def test_valid_edit_form(self, app):
        """Test edit form with valid data."""
        with app.test_request_context():
            form = AccountEditForm(
                name=TEST_DATA['account']['name'],
                account_type=TEST_DATA['account']['account_type'],
                currency=TEST_DATA['account']['currency'],
                description=TEST_DATA['account']['description']
            )
            assert form.validate()

    def test_no_initial_balance_field(self, app):
        """Test that initial_balance field is not accessible after form creation."""
        with app.test_request_context():
            form = AccountEditForm()
            # Test that initial_balance is not in the form fields
            assert 'initial_balance' not in form._fields
            # Or test that it's not rendered
            assert 'initial_balance' not in form.data

    def test_current_balance_readonly(self, app):
        """Test that current_balance field is readonly."""
        with app.test_request_context():
            form = AccountEditForm()
            assert form.current_balance.render_kw.get('readonly') is True


@pytest.mark.usefixtures('app')
class TestAccountDeleteForm:
    """Test cases for AccountDeleteForm."""

    def test_delete_form_validation(self, app):
        """Test delete form validation."""
        with app.test_request_context():
            form = AccountDeleteForm()
            assert form.validate()
