import unittest


class SerializedListTest(unittest.TestCase):

    def test_serialization(self):
        from sqlalchemy.engine.default import DefaultDialect
        from alpaca.common.persistence.types.mutable_list import MutableList
        from alpaca.common.persistence.types.serialized_list import (
            SerializedList,
        )
        dialect = DefaultDialect()
        data = [1, 2, 3, "łąki", "łan", {"foo": "bar", "łąki": "łan"}]
        mutable_list = MutableList(data)
        serialized_list = SerializedList()
        serialized = serialized_list.process_bind_param(mutable_list, dialect)
        self.assertIsInstance(serialized, bytes)
        unserialized = serialized_list.process_result_value(
            serialized,
            dialect
        )
        self.assertSequenceEqual(unserialized, data)
