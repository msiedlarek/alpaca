import unittest

from alpaca.common.tests import InterfaceTestMixin


class ModelBaseTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.domain.interfaces import IModelBase
        from alpaca.common.domain.model_base import ModelBase
        self.assertClassImplements(ModelBase, IModelBase)
        model_base = ModelBase()
        self.assertObjectImplements(model_base, IModelBase)
