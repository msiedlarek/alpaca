import unittest

from alpaca.common.tests import InterfaceTestMixin


class ProblemServiceTest(unittest.TestCase, InterfaceTestMixin):

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
        from alpaca.common.services.problem_service import (
            ProblemService,
        )
        return ProblemService(self.persistence_manager)

    def test_interface_conformity(self):
        from alpaca.common.services.interfaces import IProblemService
        from alpaca.common.services.problem_service import (
            ProblemService,
        )
        self.assertClassImplements(ProblemService, IProblemService)
        problem_service = self._get_service()
        self.assertObjectImplements(problem_service, IProblemService)
