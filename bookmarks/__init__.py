"""Main module for the application."""

import os
import logging
import base64
import binascii

from flask import Flask, g
from flask_bcrypt import Bcrypt
from flask_login import current_user, LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_marshmallow import Marshmallow
from flask_smorest import Api, abort
from flask_migrate import Migrate
from celery import Celery
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
csrf = CSRFProtect()
migrate = Migrate()
smorest_api = Api()

if os.environ.get('FLASK_ENV') == 'development':
    import config
    celery = Celery(__name__, broker=config.Development.CELERY_BROKER_URL)
elif os.environ.get('FLASK_ENV') == 'testing':
    pass
else:
    celery = Celery(__name__, broker=os.environ.get('CELERY_BROKER_URL'))

from .users.models import User


def create_app():
    """Factory function to create the Flask application."""
    app = Flask(__name__, static_url_path='/static', static_folder='templates/static')

    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.INFO)

    bcrypt.init_app(app)
    login_manager = LoginManager(app)

    app.config.from_object(f'config.{app.env.title()}')
    if app.env == 'production':
        celery.conf.update(app.config)
        if celery.conf.broker_url != app.config['CELERY_BROKER_URL']:
            raise RuntimeError("Celery url is different from app's configuration")
        # Use Sentry service
        sentry_sdk.init(dsn=app.config['SENTRY_DSN'],
                        integrations=[FlaskIntegration()])
    elif app.env == 'development':
        celery.conf.update(app.config)
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    # Database, CSRF should be attached after config is decided
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        try:
            db.create_all()
        except OperationalError:
            pass  # database/tables already exist
    ma.init_app(app)
    csrf.init_app(app)

    # Regular views
    from bookmarks.views import index
    app.register_blueprint(index)

    # API endpoints
    smorest_api.init_app(app)

    from bookmarks.api.auth import auth_api
    smorest_api.register_blueprint(auth_api)

    from bookmarks.api.helper_endpoints import helper_api
    smorest_api.register_blueprint(helper_api)

    from bookmarks.api.users import users_api
    smorest_api.register_blueprint(users_api)

    from bookmarks.api.bookmarks import bookmarks_api
    smorest_api.register_blueprint(bookmarks_api)

    from bookmarks.api.favourites import favourites_api
    smorest_api.register_blueprint(favourites_api)

    from bookmarks.api.votes import votes_api
    smorest_api.register_blueprint(votes_api)

    from bookmarks.api.subscriptions import subscriptions_api
    smorest_api.register_blueprint(subscriptions_api)

    from bookmarks.api.tags import tags_api
    smorest_api.register_blueprint(tags_api)

    @app.before_request
    def before_request():
        """Make logged in user available to Flask global variable g."""
        g.user = current_user  # this calls load_user_from_request

    @login_manager.request_loader
    def load_user_from_request(request):
        """Load user from Authorization header (tokens)."""
        # try to login using token
        token = request.headers.get('Authorization', '')
        if token.startswith('Bearer '):
            token = token.replace('Bearer ', '', 1)
            data = User.verify_auth_token(token)
            user = User.query.get(data['id']) if data else None
            if not user or user.auth_token != token:
                abort(401, message="Token is invalid")
            return user

        # next, try to login using Basic Auth
        elif token.startswith('Basic '):
            token = token.replace('Basic ', '', 1)
            try:
                email, password = base64.b64decode(token).decode('ascii').split(':')
            except (TypeError, binascii.Error):
                return None

            user = User.query.filter_by(email=email).scalar()
            if user and user.is_password_correct(password):
                return user

        # finally, return None if both methods did not login the user
        return None

    return app
