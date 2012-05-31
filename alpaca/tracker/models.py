import flask
import mongoengine as db
from flaskext.login import UserMixin
from alpaca.ext import bcrypt

class User(db.Document, UserMixin):

    username = db.StringField(max_length=50, required=True)
    password = db.StringField(max_length=60, required=True)

    meta = {
        'collection': 'users',
        'indexes': ['username',],
    }

    def set_password(self, password_plaintext):
        self.password = bcrypt.generate_password_hash(password_plaintext)

    def password_matches(self, password_plaintext):
        return bcrypt.check_password_hash(self.password, password_plaintext)

class ErrorOccurrence(db.EmbeddedDocument):
    date = db.DateTimeField(required=True)
    reporter = db.StringField(required=True)
    uri = db.StringField(max_length=2000)
    get_data = db.ListField()
    post_data = db.ListField()
    cookies = db.ListField()
    headers = db.ListField()

class Error(db.Document):
    hash = db.StringField(required=True, max_length=100, unique=True)
    summary = db.StringField(required=True)
    traceback = db.StringField(required=True)
    reporters = db.SortedListField(db.StringField())
    last_occurrence = db.DateTimeField()
    occurrence_counter = db.IntField(default=0)
    occurrence_array_size = db.IntField(default=0)
    occurrences = db.ListField(db.EmbeddedDocumentField(ErrorOccurrence))

    meta = {
        'collection': 'errors',
        'indexes': ['hash',],
    }

    @property
    def investigation_url(self):
        return flask.url_for('tracker.investigate', error_id=self.id)
