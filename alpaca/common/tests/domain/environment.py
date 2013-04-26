import unittest

from alpaca.common.tests import InterfaceTestMixin


class EnvironmentTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.domain.interfaces import IModelBase, IEnvironment
        from alpaca.common.domain.environment import Environment
        self.assertClassImplements(Environment, IModelBase)
        self.assertClassImplements(Environment, IEnvironment)
        environment = Environment()
        self.assertObjectImplements(environment, IModelBase)
        self.assertObjectImplements(environment, IEnvironment)
