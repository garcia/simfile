from collections import OrderedDict


class OrderedDictForwarder:
    _properties: "OrderedDict[str, str]"

    def __len__(self):
        return self._properties.__len__()

    def __getitem__(self, key):
        return self._properties.__getitem__(key)

    def __setitem__(self, key, value):
        return self._properties.__setitem__(key, value)

    def __delitem__(self, key):
        return self._properties.__delitem__(key)

    def __iter__(self):
        return self._properties.__iter__()

    def clear(self):
        return self._properties.clear()

    def move_to_end(self, key, last=True):
        return self._properties.move_to_end(key, last)

    def keys(self):
        return self._properties.keys()

    def values(self):
        return self._properties.values()

    def items(self):
        return self._properties.items()

    def get(self, key):
        return self._properties.get(key)
