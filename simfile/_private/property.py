from typing import Any


def attr_property(private_name, type=Any):

    @property
    def attr_property(self):
        return getattr(self, private_name)

    @attr_property.setter
    def attr_property(self, value):
        setattr(self, private_name, value)

    return attr_property


def item_property(name, type=Any):

    @property
    def item_property(self) -> type:
        return self[name]

    @attr_property.setter
    def item_property(self, value: type) -> None:
        self[name] = value

    return item_property