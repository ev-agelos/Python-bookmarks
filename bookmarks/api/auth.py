"""Auth API endpoints."""


from flask import Blueprint, g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from bookmarks import csrf
from bookmarks.users.models import User


auth_api = Blueprint('api', __name__)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')


@basic_auth.verify_password
def verify_password(email, password):
    """Verify user by email address and password."""
    g.user = User.query.filter_by(email=email).scalar()
    return g.user is not None and g.user.is_password_correct(password)


@token_auth.verify_token
def verify_token(token):
    """Verify user by token."""
    g.user = User.verify_auth_token(token)
    return g.user is not None


@auth_api.route('/api/auth/request-token', methods=['POST'])
@csrf.exempt
@basic_auth.login_required
def request_token():
    """Return new token for the user."""
    return jsonify({'token': g.user.generate_auth_token()}), 200