import unittest


class SerializedDictionaryTest(unittest.TestCase):

    def test_serialization(self):
        from sqlalchemy.engine.default import DefaultDialect
        from alpaca.common.persistence.types.mutable_dictionary import (
            MutableDictionary,
        )
        from alpaca.common.persistence.types.serialized_dictionary import (
            SerializedDictionary,
        )
        dialect = DefaultDialect()
        data = {
            "foo": "bar",
            "łąki": "łan",
            "żółw": [1, 2, "łąki"],
            "łan": {
                "łąki": "żółw",
                23: "5",
            }
        }
        mutable_dictionary = MutableDictionary(data)
        serialized_dictionary = SerializedDictionary()
        serialized = serialized_dictionary.process_bind_param(
            mutable_dictionary,
            dialect
        )
        self.assertIsInstance(serialized, bytes)
        unserialized = serialized_dictionary.process_result_value(
            serialized,
            dialect
        )
        self.assertDictEqual(unserialized, data)
