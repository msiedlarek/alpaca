import unittest
from unittest import mock


class MutableListTest(unittest.TestCase):

    def test_coerce(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        empty_mutable_list = MutableList()
        self.assertEqual(
            MutableList.coerce('baz', empty_mutable_list),
            empty_mutable_list
        )
        self.assertEqual(
            MutableList.coerce('baz', {}),
            empty_mutable_list
        )
        self.assertEqual(
            MutableList.coerce('baz', ['foo', 'bar']),
            MutableList(['foo', 'bar'])
        )
        with self.assertRaises(ValueError):
            MutableList.coerce('baz', 123)

    def test_append(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList()
        mutable_list.changed = mock.MagicMock()
        mutable_list.append(1)
        mutable_list.changed.assert_called_once_with()
        self.assertSequenceEqual(mutable_list, [1])

    def test_reverse(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList([1, 2, 3])
        mutable_list.changed = mock.MagicMock()
        mutable_list.reverse()
        mutable_list.changed.assert_called_once_with()
        self.assertSequenceEqual(mutable_list, [3, 2, 1])

    def test_extend(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList([1, 2, 3])
        mutable_list.changed = mock.MagicMock()
        mutable_list.extend([4, 5, 6])
        mutable_list.changed.assert_called_once_with()
        self.assertSequenceEqual(mutable_list, [1, 2, 3, 4, 5, 6])

    def test_pop(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList([1, 2, 3])
        mutable_list.changed = mock.MagicMock()
        result = mutable_list.pop()
        mutable_list.changed.assert_called_once_with()
        self.assertEqual(result, 3)
        self.assertSequenceEqual(mutable_list, [1, 2])

    def test_remove(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList([1, 2, 3])
        mutable_list.changed = mock.MagicMock()
        mutable_list.remove(2)
        mutable_list.changed.assert_called_once_with()
        self.assertSequenceEqual(mutable_list, [1, 3])

    def test_iadd(self):
        from alpaca.common.persistence.types.mutable_list import MutableList
        mutable_list = MutableList([1, 2, 3])
        mutable_list.changed = mock.MagicMock()
        mutable_list += [4, 5]
        mutable_list.changed.assert_called_once_with()
        self.assertSequenceEqual(mutable_list, [1, 2, 3, 4, 5])
