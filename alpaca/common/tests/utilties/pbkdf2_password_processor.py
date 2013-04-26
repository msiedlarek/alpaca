import unittest

from alpaca.common.tests import InterfaceTestMixin


class PBKDF2PasswordProcessorTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.utilities.interfaces import IPasswordProcessor
        from alpaca.common.utilities.pbkdf2_password_processor import (
            PBKDF2PasswordProcessor,
        )
        self.assertClassImplements(
            PBKDF2PasswordProcessor,
            IPasswordProcessor
        )
        password_processor = PBKDF2PasswordProcessor()
        self.assertObjectImplements(password_processor, IPasswordProcessor)

    def test_password_hashing(self):
        from alpaca.common.utilities.pbkdf2_password_processor import (
            PBKDF2PasswordProcessor,
        )
        password_processor = PBKDF2PasswordProcessor()
        hash = password_processor.get_password_hash('łąki łan 123')
        other_hash = password_processor.get_password_hash('łąki łany 123')
        hash.encode('ascii')
        other_hash.encode('ascii')
        self.assertIsInstance(hash, str)
        self.assertIsInstance(other_hash, str)
        self.assertNotEqual(hash, other_hash)
        self.assertFalse(
            password_processor.verify_password(hash, 'łąki łany 123')
        )
        self.assertTrue(
            password_processor.verify_password(hash, 'łąki łan 123')
        )
