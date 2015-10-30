"""The secret sauce to solve circual dependencies issues."""

from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
from flask_debugtoolbar import DebugToolbarExtension

from bookmarks_app import app, db
from bookmarks_app.views import index, bookmarks, bookmarks_crud, auth, users
from bookmarks_app.models import User


login_manager = LoginManager(app)
csrf = CsrfProtect(app)
toolbar = DebugToolbarExtension(app)
bookmarks.BookmarksView.register(app)
users.UsersView.register(app)


@login_manager.user_loader
def user_loader(user_id):
    """Reload the user object from the user ID stored in the session."""
    return db.query(User).get(user_id)


if __name__ == '__main__':
    app.run()
