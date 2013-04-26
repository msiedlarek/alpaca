import sys
from collections import UserDict
if sys.version_info[0] == 3 and sys.version_info[1] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping  # flake8: noqa

from sqlalchemy.ext.mutable import Mutable


class MutableDictionary(Mutable, UserDict):

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, Mapping):
                return cls(value)
            return super().coerce(key, value)
        else:
            return value

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.changed()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.changed()
        return result
