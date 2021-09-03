from typing import MutableMapping, Optional


def item_property(name, alias=None):
    
    # Decide whether to use the property's alias instead of its primary name
    def _name_or_alias(self):
        if name not in self and alias and alias in self:
            return alias
        else:
            return name

    @property
    def item_property(self: MutableMapping[str, str]) -> Optional[str]:
        return self.get(_name_or_alias(self))

    @item_property.setter
    def item_property(self: MutableMapping[str, str], value: str) -> None:
        self[_name_or_alias(self)] = value
    
    @item_property.deleter
    def item_property(self: MutableMapping[str, str]) -> None:
        del self[_name_or_alias(self)]

    return item_property