from datetime import datetime
from app.models.transaction import Transaction


def init_filters(app):
    """Initialize custom Jinja2 filters"""

    @app.template_filter('account_icon')
    def account_icon_filter(account_type):
        """Convert account type to corresponding FontAwesome icon name"""
        icons = {
            'bank': 'university',
            'cash': 'wallet',
            'credit': 'credit-card',
            'investment': 'chart-line',
            'mobile_money': 'mobile-alt',
            'other': 'coins'
        }
        return icons.get(str(account_type).lower(), 'question')


class ExportFilters:
    """Class for handling export filter parameters"""
    def __init__(self, user_id, start_date=None, end_date=None, account_id=None, format='pdf'):
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.account_id = account_id
        self.format = format

    @classmethod
    def from_request(cls, request_data, user_id):
        """Create filters from request data"""
        return cls(
            user_id=user_id,
            start_date=request_data.get('start_date'),
            end_date=request_data.get('end_date'),
            account_id=request_data.get('account_id'),
            format=request_data.get('format', 'pdf')
        )

    def build_query(self, query):
        """Apply filters to query"""
        if self.start_date:
            query = query.filter(Transaction.date >= self.start_date)
        if self.end_date:
            query = query.filter(Transaction.date <= self.end_date)
        if self.account_id:
            query = query.filter(Transaction.account_id == self.account_id)
        return query

    def get_filename(self):
        """Generate filename for export"""
        date_str = datetime.now().strftime("%Y%m%d")
        return f"spending_report_{date_str}.{self.format}"