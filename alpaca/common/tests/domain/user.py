import unittest

from alpaca.common.tests import InterfaceTestMixin


class UserTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.domain.interfaces import IModelBase, IUser
        from alpaca.common.domain.user import User
        self.assertClassImplements(User, IModelBase)
        self.assertClassImplements(User, IUser)
        user = User()
        self.assertObjectImplements(user, IModelBase)
        self.assertObjectImplements(user, IUser)

    def test_passwords(self):
        from zope.interface.registry import Components
        from alpaca.common.domain.user import User
        from alpaca.common.utilities.interfaces import IPasswordProcessor
        from alpaca.common.utilities.pbkdf2_password_processor import (
            PBKDF2PasswordProcessor
        )
        processor = PBKDF2PasswordProcessor()
        registry = Components()
        registry.registerUtility(
            processor,
            IPasswordProcessor,
            'pbkdf2'
        )
        user = User()
        user.set_password('łąki łan 123', 'pbkdf2', processor)
        self.assertEqual(user.password_processor, 'pbkdf2')
        self.assertTrue(bool(user.password_hash))
        self.assertLessEqual(len(user.password_hash), 100)
        self.assertFalse(user.password_equals('łąki łany 123', registry))
        self.assertTrue(user.password_equals('łąki łan 123', registry))
