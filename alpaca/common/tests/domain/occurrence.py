import unittest

from alpaca.common.tests import InterfaceTestMixin


class OccurrenceTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.domain.interfaces import IModelBase, IOccurrence
        from alpaca.common.domain.occurrence import Occurrence
        self.assertClassImplements(Occurrence, IModelBase)
        self.assertClassImplements(Occurrence, IOccurrence)
        occurrence = Occurrence()
        self.assertObjectImplements(occurrence, IModelBase)
        self.assertObjectImplements(occurrence, IOccurrence)
