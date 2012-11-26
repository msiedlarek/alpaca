import random
import string

import bcrypt
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy.orm import exc as database_exceptions
from zope.sqlalchemy import ZopeTransactionExtension

from alpaca import security

DBSession = orm.scoped_session(
    orm.sessionmaker(extension=ZopeTransactionExtension())
)

ModelBase = declarative_base()

def generate_random_string(length):
    return ''.join([
        random.choice(string.ascii_letters + string.digits)
        for n in xrange(length)
    ])

class Environment(ModelBase):

    __tablename__ = 'alpaca_environments'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(length=100), nullable=False, unique=True)
    api_key = sql.Column(sql.String(length=100), nullable=False)

    def regenerate_api_key(self):
        self.api_key = generate_random_string(50)

class Problem(ModelBase):

    __tablename__ = 'alpaca_problems'

    id = sql.Column(sql.Integer, primary_key=True)
    hash = sql.Column(
        sql.String(length=100),
        nullable=False,
        unique=True,
        index=True
    )
    description = sql.Column(sql.Unicode(length=5000), nullable=False)
    first_occurrence = sql.Column(sql.DateTime, nullable=False)
    last_occurrence = sql.Column(sql.DateTime, nullable=False)
    resolved = sql.Column(sql.DateTime)
    occurrence_count = sql.Column(sql.Integer, nullable=False)
    tags = sql.Column(sql.Unicode(length=1000), nullable=False, default=u'')

    def get_split_tags(self):
        return sorted(filter(
            lambda x: x,
            [tag.strip() for tag in self.tags.split(',')]
        ))

class Occurrence(ModelBase):

    __tablename__ = 'alpaca_occurrences'

    id = sql.Column(sql.Integer, primary_key=True)
    problem_id = sql.Column(
        sql.Integer,
        sql.ForeignKey('alpaca_problems.id'),
        nullable=False
    )
    environment_id = sql.Column(
        sql.Integer,
        sql.ForeignKey('alpaca_environments.id'),
        nullable=False
    )
    date = sql.Column(sql.DateTime, nullable=False)
    message = sql.Column(sql.UnicodeText, nullable=False)
    stack_trace = sql.Column(sql.PickleType)
    environment_data = sql.Column(sql.PickleType)

    problem = orm.relationship(
        'Problem',
        backref='occurrences'
    )
    environment = orm.relationship(
        'Environment',
        backref='occurrences'
    )

    def get_normalized_stack_trace(self):
        return self.stack_trace

    def get_normalized_environment_data(self):
        return self.environment_data

class User(ModelBase):

    __tablename__ = 'alpaca_users'

    id = sql.Column(sql.Integer, primary_key=True)
    email = sql.Column(sql.String(length=200), unique=True, nullable=False)
    password_hash = sql.Column(sql.String(length=100), nullable=False)

    role_user = sql.Column(sql.Boolean, nullable=False, default=True)
    role_administrator = sql.Column(sql.Boolean, nullable=False, default=False)

    _role_mapping = {
        'role_user': security.User,
        'role_administrator': security.Administrator,
    }

    @property
    def roles(self):
        return [
            principal
            for attribute_name, principal in self._role_mapping.iteritems()
            if getattr(self, attribute_name, False)
        ]

    def set_password(self, new_password):
        self.password_hash = bcrypt.hashpw(new_password, bcrypt.gensalt())

    def valid_password(self, password):
        return (
            bcrypt.hashpw(password, self.password_hash) == self.password_hash
        )

    def generate_random_password(self):
        new_password = generate_random_string(10)
        self.set_password(new_password)
        return new_password

    @classmethod
    def authentication_callback(cls, user_id, request):
        try:
            user = DBSession.query(cls).filter(
                cls.id == user_id
            ).one()
        except database_exceptions.NoResultFound:
            return None
        return user.roles
