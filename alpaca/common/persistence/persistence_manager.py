from zope import interface
import sqlalchemy as sql
from sqlalchemy import orm
from zope.sqlalchemy import ZopeTransactionExtension, mark_changed

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.persistence.insert_from_select import InsertFromSelect


@interface.implementer(IPersistenceManager)
class PersistenceManager:

    def __init__(self, settings):
        self._engine = sql.engine_from_config(settings, 'sqlalchemy.')
        self.session = orm.scoped_session(
            orm.sessionmaker(extension=ZopeTransactionExtension())
        )
        self.session.configure(bind=self._engine)

    def initialize_schema(self):
        from alpaca.common import domain  # flake8: noqa
        from alpaca.common.domain.model_base import ModelBase
        ModelBase.metadata.create_all(self._engine)

    def add_if_not_exists(self, entity, discriminator):
        table = entity.__class__.__table__
        column_names = [
            name
            for name, column in table.columns.items()
            if not column.primary_key
        ]
        query = InsertFromSelect(
            table,
            {
                getattr(table.c, column_name): getattr(entity, column_name)
                for column_name in column_names
            },
            sql.not_(sql.exists().where(
                getattr(table.c, discriminator) ==
                    getattr(entity, discriminator)
            ))
        )
        session = self.session()
        session.execute(query)
        mark_changed(session)
