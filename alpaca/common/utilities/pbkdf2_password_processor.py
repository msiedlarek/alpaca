from itertools import zip_longest

import pbkdf2
from zope import interface

from alpaca.common.utilities.interfaces import IPasswordProcessor


@interface.implementer(IPasswordProcessor)
class PBKDF2PasswordProcessor:

    _iterations = 10000

    def get_password_hash(self, password):
        return pbkdf2.crypt(password, iterations=self._iterations)

    def verify_password(self, correct_password_hash, alleged_password):
        alleged_hash = pbkdf2.crypt(alleged_password, correct_password_hash)
        diff = 0
        for a, b in zip_longest(correct_password_hash, alleged_hash):
            diff |= ord(a) ^ ord(b)
        return diff == 0
