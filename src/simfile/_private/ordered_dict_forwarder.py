from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional, Sequence, Set, Union

from msdparser import MSDParameter


OrderedDictType = Union[OrderedDict[str, str], "OrderedDictForwarder"]


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

    def clear_properties(self):
        return self._properties.clear()

    def copy_properties(self):
        return self._properties.copy()

    def update_properties(self, other: Union[OrderedDict, "OrderedDictForwarder"]):
        self._properties.update(other)

    def move_to_end(self, key, last=True):
        return self._properties.move_to_end(key, last)

    def keys(self):
        return self._properties.keys()

    def values(self):
        return self._properties.values()

    def items(self):
        return self._properties.items()

    def get(self, key: str):
        return self._properties.get(key)

    def pop(self, key: str):
        return self._properties.pop(key)


@dataclass
class Property:
    value: str
    msd_parameter: MSDParameter


OrderedDictPropertyType = Union[
    OrderedDict[str, Property], "OrderedDictPropertyForwarder"
]


class OrderedDictPropertyForwarder:
    _properties: OrderedDict[str, Property]
    _default_property: Property

    def __len__(self):
        return self._properties.__len__()

    def __getitem__(self, key):
        property = self._properties.__getitem__(key)
        return property.value if property else None

    def __setitem__(self, key, value: str):
        try:
            property: Property = self._properties.__getitem__(key)
        except KeyError:
            property = deepcopy(self._default_property)
            self._properties.__setitem__(key, property)
        property.value = value

    def __delitem__(self, key):
        return self._properties.__delitem__(key)

    def __iter__(self):
        return self._properties.__iter__()

    def move_to_end(self, key, last=True):
        return self._properties.move_to_end(key, last)

    def keys(self):
        return self._properties.keys()

    def values(self) -> Sequence[str]:
        return [property.value for property in self._properties.values()]

    def items(self) -> Sequence[tuple[str, str]]:
        return [(key, property.value) for key, property in self._properties.items()]

    def get(self, key: str) -> Optional[str]:
        property = self._properties.get(key)
        return property.value if property else None

    def pop(self, key: str) -> str:
        return self._properties.pop(key).value
