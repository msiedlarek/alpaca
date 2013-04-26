from zope import interface
import sqlalchemy as sql

from alpaca.common.domain.interfaces import IEnvironment
from alpaca.common.domain.model_base import ModelBase


@interface.implementer(IEnvironment)
class Environment(ModelBase):

    __tablename__ = 'alpaca_environments'

    name = sql.Column(
        sql.String(length=100),
        nullable=False,
        index=True,
        unique=True
    )
