import unittest

from alpaca.common.tests import InterfaceTestMixin


class RandomGeneratorTest(unittest.TestCase, InterfaceTestMixin):

    def test_interface_conformity(self):
        from alpaca.common.utilities.interfaces import IRandomGenerator
        from alpaca.common.utilities.random_generator import RandomGenerator
        self.assertClassImplements(RandomGenerator, IRandomGenerator)
        random_generator = RandomGenerator()
        self.assertObjectImplements(random_generator, IRandomGenerator)

    def test_correct_length(self):
        from alpaca.common.utilities.random_generator import RandomGenerator
        random_generator = RandomGenerator()
        for length in range(50):
            self.assertEqual(
                len(random_generator(length)),
                length
            )

    def test_correct_character_set(self):
        import re
        from alpaca.common.utilities.random_generator import RandomGenerator
        correct_re = re.compile(r'^[A-Za-z0-9]*$')
        random_generator = RandomGenerator()
        for length in range(50):
            self.assertRegex(
                random_generator(length),
                correct_re
            )
