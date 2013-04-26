import random
import string

from zope import interface

from alpaca.common.utilities.interfaces import IRandomGenerator


@interface.implementer(IRandomGenerator)
class RandomGenerator:

    def __call__(self, length):
        return ''.join((
            random.choice(string.ascii_letters + string.digits)
            for n in range(length)
        ))
