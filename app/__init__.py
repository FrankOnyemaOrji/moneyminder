from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
moment = Moment()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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
        from .routes.categories import categories
        from .routes.budgets import budgets

        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(main)
        app.register_blueprint(accounts, url_prefix='/accounts')
        app.register_blueprint(transactions, url_prefix='/transactions')
        app.register_blueprint(categories, url_prefix='/categories')
        app.register_blueprint(budgets, url_prefix='/budgets')

        @login_manager.user_loader
        def load_user(user_id):
            return User.get_by_id(user_id)

    return app
