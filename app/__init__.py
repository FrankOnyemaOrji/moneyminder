from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect

# Initialize Flask extensions
from app.models import db

migrate = Migrate()
login_manager = LoginManager()


def register_filters(app):
    @app.template_filter('date')
    def date_filter(value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime('%Y-%m-%d')


def create_app(config_class=None):
    app = Flask(__name__, static_url_path='/static',
                static_folder='static')

    # Load config
    if config_class is None:
        from .config import Config
        config_class = Config
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment = Moment(app)
    csrf = CSRFProtect(app)

    app.app_context().push()

    # Setup Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import filters and models after db is initialized
        from app.utils.filters import init_filters
        init_filters(app)
        register_filters(app)

        from app.models import User, Account, Category, Transaction, Budget
        from .models.category import Category

        @app.context_processor
        def utility_processor():
            return {'Category': Category}

        db.create_all()

        # Register blueprints
        from .routes.auth import auth
        from .routes.main import main
        from .routes.accounts import accounts
        from .routes.transactions import transactions
        from .routes.budgets import budgets
        from .routes.reports import bp as reports_bp

        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(main)
        app.register_blueprint(accounts, url_prefix='/accounts')
        app.register_blueprint(transactions, url_prefix='/transactions')
        app.register_blueprint(budgets, url_prefix='/budgets')
        app.register_blueprint(reports_bp)

        @login_manager.user_loader
        def load_user(user_id):
            return User.get_by_id(user_id)

    return app
