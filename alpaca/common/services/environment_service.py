from zope import (
    interface,
    component,
)
from sqlalchemy.orm import exc as db_exc

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.services.interfaces import IEnvironmentService
from alpaca.common.domain.environment import Environment
from alpaca.common.domain.occurrence import Occurrence


@component.adapter(IPersistenceManager)
@interface.implementer(IEnvironmentService)
class EnvironmentService:

    def __init__(self, persistence_manager):
        self._persistence_manager = persistence_manager

    def create_environment(self, environment):
        self._persistence_manager.session.add(environment)
        return environment

    def delete_environment(self, environment):
        self._persistence_manager.session.delete(environment)

    def get_environment(self, id):
        try:
            return self._persistence_manager.session.query(
                Environment
            ).filter(
                Environment.id == id
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_environment_by_name(self, name):
        try:
            return self._persistence_manager.session.query(
                Environment
            ).filter(
                Environment.name == name
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_all_environments(self):
        return self._persistence_manager.session.query(
            Environment
        ).order_by(
            Environment.name
        )

    def get_affected_environments(self, problem):
        return self._persistence_manager.session.query(
            Environment
        ).distinct().join(
            Occurrence
        ).filter(
            Occurrence.problem == problem
        ).order_by(
            Environment.name
        )
