import sys
from collections import UserList
if sys.version_info[0] == 3 and sys.version_info[1] < 3:
    from collections import Iterable
else:
    from collections.abc import Iterable  # flake8: noqa

from sqlalchemy.ext.mutable import Mutable


class MutableList(Mutable, UserList):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, Iterable):
                return cls(value)
            return super().coerce(key, value)
        else:
            return value

    def append(self, *args, **kwargs):
        result = super().append(*args, **kwargs)
        self.changed()
        return result

    def reverse(self, *args, **kwargs):
        result = super().reverse(*args, **kwargs)
        self.changed()
        return result

    def extend(self, *args, **kwargs):
        result = super().extend(*args, **kwargs)
        self.changed()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.changed()
        return result

    def remove(self, *args, **kwargs):
        result = super().remove(*args, **kwargs)
        self.changed()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.changed()
        return result

    def __iadd__(self, *args, **kwargs):
        result = super().__iadd__(*args, **kwargs)
        self.changed()
        return result
