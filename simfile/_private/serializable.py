from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import Callable, Generic, Optional, TextIO, TypeVar


T = TypeVar('T')
class Serializable(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, file: TextIO) -> Optional[str]:
        pass

    @staticmethod
    def enable_string_output(serialize_impl: Callable[[T, TextIO], None]) -> \
            Callable[[T, Optional[TextIO]], Optional[str]]:
        def serialize(self: T, file: Optional[TextIO] = None) -> Optional[str]:
            if file:
                return serialize_impl(self, file)
            stringio = StringIO()
            serialize_impl(self, stringio)
            return stringio.getvalue()
        return serialize