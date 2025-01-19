from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.utils.filters import init_filters
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# moment = Moment()

from datetime import datetime


def register_filters(app):
    @app.template_filter('date')
    def date_filter(value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime('%Y-%m-%d')


def create_app():
    app = Flask(__name__)
    init_filters(app)
    app.config.from_object(Config)
    moment = Moment(app)

    @app.context_processor
    def utility_processor():
        return {
            'Category': Category
        }

    register_filters(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment.init_app(app)

    # Setup Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models and create tables
        from .models import User, Account, Category, Transaction, Budget
        db.create_all()

        # Register blueprints
        from .routes.auth import auth
        from .routes.main import main
        from .routes.accounts import accounts
        from .routes.transactions import transactions
        from .routes.budgets import budgets

        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(main)
        app.register_blueprint(accounts, url_prefix='/accounts')
        app.register_blueprint(transactions, url_prefix='/transactions')
        app.register_blueprint(budgets, url_prefix='/budgets')

        @login_manager.user_loader
        def load_user(user_id):
            return User.get_by_id(user_id)

    return app
