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
