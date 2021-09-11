from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import TextIO


class Serializable(metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, file: TextIO) -> None:
        """
        Write the object to provided text file object as MSD.
        """
        pass
    
    def __str__(self) -> str:
        """
        Convert the object to an MSD string.
        """
        serialized = StringIO()
        self.serialize(serialized)
        return serialized.getvalue()