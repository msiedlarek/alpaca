import unittest
from unittest.mock import MagicMock

from pyramid import testing

from alpaca.common.tests import InterfaceTestMixin


class LayoutTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.frontend.interfaces import ILayout
        from alpaca.frontend.layout import Layout
        self.assertClassImplements(Layout, ILayout)
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        request.route_path = MagicMock()
        request.static_path = MagicMock()
        layout = Layout(request.context, request)
        self.assertObjectImplements(layout, ILayout)
