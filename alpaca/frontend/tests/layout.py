import unittest

from mock import MagicMock
from pyramid import testing

from alpaca.common.tests import InterfaceTestMixin
from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.services.interfaces import IEnvironmentService
from alpaca.common.services.environment_service import EnvironmentService


class LayoutTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.frontend.interfaces import ILayout
        from alpaca.frontend.layout import Layout
        self.assertClassImplements(Layout, ILayout)
        request = self._get_request()
        layout = Layout(request.context, request)
        self.assertObjectImplements(layout, ILayout)

    def _get_request(self):
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        request.route_path = MagicMock()
        request.static_path = MagicMock()
        request.persistence_manager = self._get_persistence_manager()
        request.registry.registerAdapter(
            EnvironmentService,
            (IPersistenceManager,),
            IEnvironmentService
        )
        return request

    def _get_persistence_manager(self):
        from alpaca.common.persistence.persistence_manager import (
            PersistenceManager,
        )
        persistence_manager = PersistenceManager({
            'sqlalchemy.url': 'sqlite://',
        })
        persistence_manager.initialize_schema()
        return persistence_manager
