from zope import interface
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

from alpaca.common.domain.interfaces import IModelBase

DeclarativeBase = declarative_base(name='DeclarativeBase')


@interface.implementer(IModelBase)
class ModelBase(DeclarativeBase):

    __abstract__ = True

    id = sql.Column(sql.Integer, primary_key=True)
