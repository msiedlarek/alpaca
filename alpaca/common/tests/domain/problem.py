import unittest

from alpaca.common.tests import InterfaceTestMixin


class ProblemTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.domain.interfaces import IModelBase, IProblem
        from alpaca.common.domain.problem import Problem
        self.assertClassImplements(Problem, IModelBase)
        self.assertClassImplements(Problem, IProblem)
        problem = Problem()
        self.assertObjectImplements(problem, IModelBase)
        self.assertObjectImplements(problem, IProblem)
