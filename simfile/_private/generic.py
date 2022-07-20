from collections import UserList
from typing import MutableSequence, TypeVar

E = TypeVar("E")


class ListWithRepr(UserList, MutableSequence[E]):
    """
    Subclass of UserList with type hints and some overrides for convenience.
    """

    def __repr__(self) -> str:
        return "%s(%s)" % (self.__class__.__name__, super().__repr__())
