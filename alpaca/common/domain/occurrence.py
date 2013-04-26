from zope import interface
import sqlalchemy as sql
from sqlalchemy import orm

from alpaca.common.persistence.types.serialized_list import (
    SerializedList
)
from alpaca.common.persistence.types.serialized_dictionary import (
    SerializedDictionary
)
from alpaca.common.domain.interfaces import IOccurrence
from alpaca.common.domain.model_base import ModelBase
from alpaca.common.domain.problem import Problem
from alpaca.common.domain.environment import Environment


@interface.implementer(IOccurrence)
class Occurrence(ModelBase):

    __tablename__ = 'alpaca_occurrences'

    problem_id = sql.Column(
        sql.BigInteger,
        sql.ForeignKey('alpaca_problems.id'),
        nullable=False
    )
    environment_id = sql.Column(
        sql.BigInteger,
        sql.ForeignKey('alpaca_environments.id'),
        nullable=False
    )
    date = sql.Column(
        sql.DateTime,
        nullable=False
    )
    message = sql.Column(
        sql.Text,
        nullable=False
    )
    stack_trace = sql.Column(
        SerializedList
    )
    environment_data = sql.Column(
        SerializedDictionary
    )

    problem = orm.relationship(
        Problem,
        backref=orm.backref('occurrences')
    )
    environment = orm.relationship(
        Environment,
        backref=orm.backref('occurrences')
    )
