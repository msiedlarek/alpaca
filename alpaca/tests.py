import unittest

from pyramid import testing

from alpaca.models import DBSession

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import ModelBase
        DBSession.configure(bind=engine)
        ModelBase.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from alpaca.views.problems import dashboard
        request = testing.DummyRequest()
        info = dashboard(request)
        self.assertEqual(info, {})
