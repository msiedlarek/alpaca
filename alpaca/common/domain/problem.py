from zope import interface
import sqlalchemy as sql

from alpaca.common.domain.interfaces import IProblem
from alpaca.common.domain.model_base import ModelBase
from alpaca.common.persistence.types.utc_datetime import UTCDateTime
from alpaca.common.persistence.types.serialized_list import SerializedList


@interface.implementer(IProblem)
class Problem(ModelBase):

    __tablename__ = 'alpaca_problems'

    hash = sql.Column(
        sql.LargeBinary(length=16),
        nullable=False,
        unique=True,
        index=True
    )
    description = sql.Column(
        sql.String(length=5000),
        nullable=False
    )
    first_occurrence = sql.Column(
        UTCDateTime,
        nullable=False
    )
    last_occurrence = sql.Column(
        UTCDateTime,
        nullable=False
    )
    resolved = sql.Column(
        UTCDateTime
    )
    occurrence_count = sql.Column(
        sql.BigInteger,
        nullable=False
    )
    tags = sql.Column(
        SerializedList,
        nullable=False,
        default=[]
    )
