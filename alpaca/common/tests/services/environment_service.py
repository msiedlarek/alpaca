import unittest

from alpaca.common.tests import InterfaceTestMixin


class EnvironmentServiceTest(unittest.TestCase, InterfaceTestMixin):

    def setUp(self):
        from alpaca.common.persistence.persistence_manager import (
            PersistenceManager,
        )
        self.persistence_manager = PersistenceManager({
            'sqlalchemy.url': 'sqlite://',
        })
        self.persistence_manager.initialize_schema()

    def tearDown(self):
        self.persistence_manager.session.remove()

    def _get_service(self):
        from alpaca.common.services.environment_service import (
            EnvironmentService,
        )
        return EnvironmentService(self.persistence_manager)

    def test_interface_conformity(self):
        from alpaca.common.services.interfaces import IEnvironmentService
        from alpaca.common.services.environment_service import (
            EnvironmentService,
        )
        self.assertClassImplements(EnvironmentService, IEnvironmentService)
        environment_service = self._get_service()
        self.assertObjectImplements(environment_service, IEnvironmentService)

    def test_create_and_get_environment(self):
        import transaction
        from alpaca.common.domain.environment import Environment
        service = self._get_service()
        environment = Environment(name="łąka")
        with transaction.manager:
            service.create_environment(environment)
            self.persistence_manager.session.flush()
            id = environment.id
        self.assertIsNotNone(id)
        saved_environment = service.get_environment(id)
        self.assertEqual(saved_environment.name, "łąka")
        self.assertIsNone(service.get_environment(id + 1))

    def test_get_environment_by_name(self):
        import transaction
        from alpaca.common.domain.environment import Environment
        service = self._get_service()
        environment = Environment(name="łąka")
        with transaction.manager:
            service.create_environment(environment)
            self.persistence_manager.session.flush()
            id = environment.id
        result = service.get_environment_by_name("łąka")
        self.assertEqual(result.id, id)
        self.assertEqual(result.name, "łąka")
        self.assertIsNone(service.get_environment_by_name("żółw"))
