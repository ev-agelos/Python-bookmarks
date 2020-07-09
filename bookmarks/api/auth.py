"""Auth API endpoints."""


from flask import g, url_for, current_app
from flask_smorest import abort, Blueprint
from flask_login import login_required, logout_user

from bookmarks import csrf, db, utils
from bookmarks.users.models import User

from .schemas import UserPOSTSchema, TokenSchema
from .utils import is_recaptcha_valid


auth_api = Blueprint('auth_api', 'Auth', url_prefix='/api/v1/auth/',
                     description='Endpoints for logging in/out etc')


@auth_api.route('/request-token', methods=['POST'])
@csrf.exempt
@login_required
def request_token():
    """Return new token for the user."""
    if not g.user.active:
        abort(403, message='Email address is not verified yet.')
    # TODO check if need to call login_user, also research what authenticated = True does (cause it is not called)
    return {'token': g.user.generate_auth_token()}


@auth_api.route('/confirm')
@auth_api.arguments(TokenSchema, location='query')
@csrf.exempt
def confirm(args):
    data = User.verify_auth_token(args['token'])
    user = User.query.get(data['id']) if data.get('id') else None
    if user is None:
        abort(409, message='Confirmation link is invalid or has expired.')

    if 'email' in data:  # user tried to update profile
        user_exists = User.query.filter_by(email=data['email']).scalar()
        if user_exists:
            abort(409, message='Email is already taken')
        user.email = data['email']
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        return {'message': ('Email updated successfully. You can now login with the new '
                            'email address.')}, 200

    if user.active:
        return {'message': 'Your account is already activated, please login.'}, 200

    user.active = True
    db.session.add(user)
    db.session.commit()
    return {'message': 'Your account has been activated. You can now login.'}, 200


@auth_api.route('/logout')
@csrf.exempt
@login_required
def logout():
    """Logout a user."""
    g.user.auth_token = ''
    g.user.authenticated = False
    logout_user()
    db.session.commit()
    return {}, 204


@auth_api.route('/register', methods=['POST'])
@csrf.exempt
@auth_api.arguments(UserPOSTSchema)
def register(args):
    user = db.session.query(User).filter(
        (User.username == args['username']) |
        (User.email == args['email'])).first()
    if user and user.username == args['username'] and \
            user.email == args['email']:
        abort(409, message='Username and email are already taken')
    if user and user.username == args['username']:
        abort(409, message='Username is already taken')
    if user and user.email == args['email']:
        abort(409, message='Email is already taken')

    if not is_recaptcha_valid(args['recaptcha']):
        abort(409, message="Recaptcha verification failed")

    user = User(username=args['username'], email=args['email'],
                password=args['password'])
    db.session.add(user)
    db.session.commit()
    user.auth_token = user.generate_auth_token()
    db.session.add(user)
    db.session.commit()
    activation_link = url_for('auth_api.confirm', token=user.auth_token,
                              _external=True)
    text = (f'Welcome {user.username},\n\nactivate your account by clicking this'
            f' link: {activation_link}')
    utils.send_email('Account confirmation - PyBook', user.email, text)
    return {'message': ('A verification email has been sent to the registered '
                        'email address. Please follow the instructions to verify'
                        ' your email address.')}, 200
