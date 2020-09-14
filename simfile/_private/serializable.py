from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import Callable, Generic, Optional, TextIO, TypeVar


T = TypeVar('T')
class Serializable(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, file: TextIO) -> Optional[str]:
        pass
    
    def __str__(self):
        serialized = StringIO()
        self.serialize(serialized)
        return serialized.getvalue()