import pytest
from datetime import datetime, timedelta
from app.utils.filters import ExportFilters, init_filters
from app.models import Transaction


@pytest.mark.usefixtures('app')
class TestExportFilters:
    """Test cases for ExportFilters."""

    def test_filter_creation(self):
        """Test filter creation with valid data."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        filters = ExportFilters(
            user_id='test-user',
            start_date=start_date,
            end_date=end_date,
            account_id='test-account',
            format='pdf'
        )
        assert filters.user_id == 'test-user'
        assert filters.format == 'pdf'
        assert filters.start_date == start_date
        assert filters.end_date == end_date

    def test_filter_from_request(self):
        """Test creating filters from request data."""
        request_data = {
            'start_date': datetime(2025, 1, 1),
            'end_date': datetime(2025, 12, 31),
            'account_id': 'test-account',
            'format': 'xlsx'
        }
        
        filters = ExportFilters.from_request(request_data, 'test-user')
        assert filters.user_id == 'test-user'
        assert filters.format == 'xlsx'
        assert isinstance(filters.start_date, datetime)
        assert isinstance(filters.end_date, datetime)

    def test_query_building(self, database, test_user, test_transaction):
        """Test query building with filters."""
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        
        filters = ExportFilters(
            user_id=test_user.id,
            start_date=start_date,
            end_date=end_date,
            account_id=test_transaction.account_id
        )

        # Build and execute query
        query = Transaction.query
        filtered_query = filters.build_query(query)
        results = filtered_query.all()

        assert test_transaction in results

    def test_date_validation(self):
        """Test date handling in filters."""
        # Test end date before start date is allowed
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now()

        filters = ExportFilters(
            user_id='test-user',
            start_date=start_date,
            end_date=end_date
        )
        # Verify dates are stored as provided
        assert filters.start_date == start_date
        assert filters.end_date == end_date

        # Test dates far in future are allowed
        start_date = datetime.now() + timedelta(days=366)
        end_date = datetime.now() + timedelta(days=367)

        filters = ExportFilters(
            user_id='test-user',
            start_date=start_date,
            end_date=end_date
        )
        assert filters.start_date == start_date
        assert filters.end_date == end_date

    def test_invalid_format(self):
        """Test format handling."""
        # Test that any format is accepted
        filters = ExportFilters(
            user_id='test-user',
            format='invalid'
        )
        # Verify format is stored as provided
        assert filters.format == 'invalid'

        # Test default format
        filters = ExportFilters(user_id='test-user')
        assert filters.format == 'pdf'


@pytest.mark.usefixtures('app')
class TestTemplateFilters:
    """Test cases for template filters."""

    def test_account_icon_filter(self, app):
        """Test account icon filter."""
        with app.app_context():
            init_filters(app)
            assert app.jinja_env.filters['account_icon']('bank') == 'university'
            assert app.jinja_env.filters['account_icon']('unknown') == 'question'

    @pytest.mark.parametrize('account_type,expected_icon', [
        ('bank', 'university'),
        ('cash', 'wallet'),
        ('credit', 'credit-card'),
        ('investment', 'chart-line'),
        ('mobile_money', 'mobile-alt'),
        ('other', 'coins'),
        ('unknown', 'question')
    ])
    def test_account_icons(self, app, account_type, expected_icon):
        """Test all account type icons."""
        with app.app_context():
            init_filters(app)
            assert app.jinja_env.filters['account_icon'](account_type) == expected_icon

    def test_filter_chaining(self, app):
        """Test filter chaining in templates."""
        with app.app_context():
            init_filters(app)
            template = "{{ account_type|account_icon|upper }}"
            rendered = app.jinja_env.from_string(template).render(
                account_type='bank'
            )
            assert rendered == 'UNIVERSITY'

    def test_filter_with_none(self, app):
        """Test filters with None values."""
        with app.app_context():
            init_filters(app)
            assert app.jinja_env.filters['account_icon'](None) == 'question'

    def test_empty_string(self, app):
        """Test filters with empty string."""
        with app.app_context():
            init_filters(app)
            assert app.jinja_env.filters['account_icon']('') == 'question'

    def test_filter_registration(self, app):
        """Test filter registration."""
        with app.app_context():
            # Reset filters
            app.jinja_env.filters.pop('account_icon', None)
            
            # Initialize filters
            init_filters(app)
            
            # Verify filter is registered
            assert 'account_icon' in app.jinja_env.filters
