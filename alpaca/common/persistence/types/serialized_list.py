from sqlalchemy.types import TypeDecorator, LargeBinary
import msgpack

from alpaca.common.persistence.types.mutable_list import MutableList


class SerializedList(TypeDecorator):

    impl = LargeBinary
    encoding = 'utf-8'

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = msgpack.packb(value.data, encoding=self.encoding)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = msgpack.loads(value, encoding=self.encoding)
        return value


MutableList.associate_with(SerializedList)
