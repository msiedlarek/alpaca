import unittest

from alpaca.common.tests import InterfaceTestMixin


class PersistenceManagerTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.persistence.interfaces import IPersistenceManager
        from alpaca.common.persistence.persistence_manager import (
            PersistenceManager,
        )
        self.assertClassImplements(PersistenceManager, IPersistenceManager)
        persistence_manager = self.__get_test_manager()
        self.assertObjectImplements(persistence_manager, IPersistenceManager)

    def __get_test_manager(self):
        from alpaca.common.persistence.persistence_manager import (
            PersistenceManager,
        )
        return PersistenceManager({
            'sqlalchemy.url': 'sqlite://',
        })
