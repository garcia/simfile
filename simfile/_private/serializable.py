from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import Optional, TextIO


class Serializable(metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, file: TextIO) -> Optional[str]:
        pass
    
    def __str__(self):
        serialized = StringIO()
        self.serialize(serialized)
        return serialized.getvalue()