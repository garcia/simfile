from typing import Any, MutableMapping, Optional, cast


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