from typing import Any, MutableMapping, Optional


def attr_property(private_name, type=str):

    @property
    def attr_property(self):
        return getattr(self, private_name)

    @attr_property.setter
    def attr_property(self, value):
        setattr(self, private_name, value)

    return attr_property


def item_property(name):

    @property
    def item_property(self: MutableMapping[str, str]) -> Optional[str]:
        return self.get(name)

    @item_property.setter
    def item_property(self: MutableMapping[str, str], value: str) -> None:
        self[name] = value
    
    @item_property.deleter
    def item_property(self: MutableMapping[str, str]) -> None:
        del self[name]

    return item_property