"""Create the database schema for the application."""


from sqlalchemy.ext.hybrid import hybrid_property

from bookmarks_app import db, bcrypt
from .schemas import (UserSchema, CategorySchema, BookmarkSchema, VoteSchema,
                      SaveBookmarkSchema)


class User(db.Model):
    """
    Define columns for User table.

    backref: adds attribute to Bookmark instance to use it like: bookmark.user
    cascade: delete all bookmarks related to User when User is deleted
    lazy: return a query object which you can refine further like if you want
        to add a limit etc
    """
    __tablename__ = 'users'

    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    email = db.Column(db.String(30))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())
    _password = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=False)
    bookmarks = db.relationship('Bookmark', backref='users',
                                cascade='all, delete-orphan', lazy='dynamic')

    @hybrid_property
    def password(self):
        """Getter for password."""
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        """Setter for password."""
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_password_correct(self, plaintext):
        """Check if user's password is correct."""
        return bcrypt.check_password_hash(self._password, plaintext)

    def is_active(self):
        """Return if user is active or not."""
        return self.active

    def get_id(self):
        """Return a unique identifier for a user instance."""
        return self._id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        """Representation of a User instance."""
        return '<User {}>'.format(self.username)

    def serialize(self):
        """Return object serialized according to it's schema."""
        schema = UserSchema()
        return schema.dump(self)


class Category(db.Model):
    """Define column for bookmark categories."""

    __tablename__ = 'categories'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=True, unique=True,
                     default='Uncategorized')

    def serialize(self):
        """Return object serialized according to it's schema."""
        schema = CategorySchema()
        return schema.dump(self)

    def __repr__(self):
        """Representation of a Category instance."""
        return '<Category {}>'.format(self.name)


class Bookmark(db.Model):
    """"Define columns for bookmarks table."""

    __tablename__ = 'bookmarks'

    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    url = db.Column(db.String, unique=True)
    rating = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())
    thumbnail = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories._id'))

    def serialize(self):
        """Return object serialized according to it's schema."""
        schema = BookmarkSchema()
        return schema.dump(self)

    def __repr__(self):
        """Representation of a Bookmark instance."""
        return '<Bookmark {}>'.format(self.title)


class Vote(db.Model):
    """Define what each user voted for each bookmark."""

    __tablename__ = 'votes'

    _id = db.Column(db.Integer, primary_key=True)
    direction = db.Column(db.Boolean, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks._id'))

    def serialize(self):
        """Return object serialized according to it's schema."""
        schema = VoteSchema()
        return schema.dump(self)

    def __repr__(self):
        """Representation of a Vote instance."""
        return '<Vote {}>'.format(self.direction)


class SaveBookmark(db.Model):
    """Define what bookmarks each user saved."""

    __tablename__ = 'savebookmark'

    _id = db.Column(db.Integer, primary_key=True)
    is_saved = db.Column(db.Boolean, default=True)
    saved_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks._id'))

    def serialize(self):
        """Return object serialized according to it's schema."""
        schema = SaveBookmarkSchema()
        return schema.dump(self)

    def __repr__(self):
        """Representation of a SaveBookmark instance."""
        return '<SaveBookmark {}>'.format(self.saved_on)
