from collections import UserList
from typing import Iterable, List, Optional, TypeVar

E = TypeVar("E")


class ListWithRepr(List[E]):
    """
    Subclass of UserList with type hints and some overrides for convenience.
    """

    def __init__(self, items: Optional[Iterable[E]] = None):
        if items:
            super().__init__(items)
        else:
            super().__init__()

    def __repr__(self) -> str:
        return "%s(%s)" % (self.__class__.__name__, super().__repr__())
