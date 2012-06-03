import flask
import mongoengine as db
from flaskext.login import UserMixin
from alpaca.ext import bcrypt

class User(db.Document, UserMixin):

    username = db.StringField(max_length=50, required=True, unique=True)
    password = db.StringField(max_length=60, required=True)

    meta = {
        'collection': 'users',
        'indexes': ['username',],
    }

    def set_password(self, password_plaintext):
        self.password = bcrypt.generate_password_hash(password_plaintext)

    def password_matches(self, password_plaintext):
        return bcrypt.check_password_hash(self.password, password_plaintext)

class StackFrame(db.EmbeddedDocument):
    filename = db.StringField()
    line_number = db.IntField()
    function = db.StringField()
    pre_context = db.ListField(db.StringField())
    context = db.StringField()
    post_context = db.ListField(db.StringField())
    variables = db.DictField()

class ErrorOccurrence(db.EmbeddedDocument):
    date = db.DateTimeField(required=True)
    stack_trace = db.ListField(db.EmbeddedDocumentField(StackFrame))
    reporter = db.StringField(required=True)
    uri = db.StringField(max_length=2000)
    get_data = db.ListField()
    post_data = db.ListField()
    cookies = db.ListField()
    headers = db.ListField()

class Error(db.Document):
    hash = db.StringField(required=True, max_length=100, unique=True)
    message = db.StringField(required=True)
    reporters = db.SortedListField(db.StringField())
    last_occurrence = db.DateTimeField()
    occurrence_counter = db.IntField(default=0)
    occurrence_array_size = db.IntField(default=0)
    occurrences = db.ListField(db.EmbeddedDocumentField(ErrorOccurrence))
    tags = db.SortedListField(db.StringField())

    meta = {
        'collection': 'errors',
        'indexes': ['hash', 'last_occurrence',],
    }

    @property
    def summary(self):
        return self.message.split('\n')[0].strip()

    @property
    def investigation_url(self):
        return flask.url_for('tracker.investigate', error_id=self.id)
