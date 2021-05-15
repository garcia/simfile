from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import Optional, TextIO


class Serializable(metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, file: TextIO) -> Optional[str]:
        """
        Write the object to provided text file object as MSD.
        """
        pass
    
    def __str__(self):
        """
        Convert the object to an MSD string.
        """
        serialized = StringIO()
        self.serialize(serialized)
        return serialized.getvalue()