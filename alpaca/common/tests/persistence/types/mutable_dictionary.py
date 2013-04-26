import unittest
from unittest import mock


class MutableDictionaryTest(unittest.TestCase):

    def test_coerce(self):
        from alpaca.common.persistence.types.mutable_dictionary import (
            MutableDictionary,
        )
        empty_mutable_dictionary = MutableDictionary()
        self.assertEqual(
            MutableDictionary.coerce('baz', empty_mutable_dictionary),
            empty_mutable_dictionary
        )
        self.assertEqual(
            MutableDictionary.coerce('baz', {}),
            empty_mutable_dictionary
        )
        self.assertEqual(
            MutableDictionary.coerce('baz', {'foo': 'bar'}),
            MutableDictionary({'foo': 'bar'})
        )
        bad_type_values = (
            'foobar',
            b'foobar',
            123,
            ['foo', 'bar', 'baz'],
        )
        for bad_type_value in bad_type_values:
            with self.assertRaises(ValueError):
                MutableDictionary.coerce('baz', bad_type_value)

    def test_setitem(self):
        from alpaca.common.persistence.types.mutable_dictionary import (
            MutableDictionary,
        )
        dictionary = MutableDictionary()
        dictionary.changed = mock.MagicMock()
        dictionary['test'] = 1
        dictionary.changed.assert_called_once_with()

    def test_delitem(self):
        from alpaca.common.persistence.types.mutable_dictionary import (
            MutableDictionary,
        )
        dictionary = MutableDictionary()
        dictionary['test'] = 1
        dictionary.changed = mock.MagicMock()
        del dictionary['test']
        dictionary.changed.assert_called_once_with()
