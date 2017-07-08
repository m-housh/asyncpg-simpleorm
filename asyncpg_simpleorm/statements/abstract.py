import abc
import typing
import weakref

from ..abstract import _all_checks


class StatementABC(metaclass=abc.ABCMeta):
    """Abstract representation of a database query statement.

    """
    __slots__ = ()

    @property
    @abc.abstractmethod
    def model(self):  # pragma: no cover
        """Return the model set on an instance.

        """
        pass

    @abc.abstractmethod
    def query_string(self, sep='\n') -> str:  # pragma: no cover
        """Return the query string set on an instance.

        """
        pass

    @abc.abstractmethod
    def query_args(self) -> typing.Iterable[typing.Any]:  # pragma: no cover
        """Return the query arguments set on an instance.

        """
        pass

    @abc.abstractmethod
    def query(self) -> typing.Iterable[typing.Any]:  # pragma: no cover
        """Return an iterable that can be used in an ``asyncpg`` query.
        The first value should be the ``query_string``, followed by the
        flattened query args.

        """
        pass

    @abc.abstractmethod
    def set_statement(self, *args, **kwargs):  # pragma: no cover
        """Set the statement on the instance.

        """
        pass

    def __iter__(self) -> typing.Iterator[typing.Any]:  # pragma: no cover
        return iter(self.query())

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is StatementABC:
            return _all_checks(Cls, 'model', 'query_string', 'query_args',
                               'set_statement', '__iter__')
        return NotImplemented  # pragma: no cover


class SimpleDescriptor:
    """Simple transparent descriptor that uses a
    :class:`weakref.WeakKeyDictionary` to store instance values.

    """
    __slots__ = ('_values')

    def __init__(self):
        self._values = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(instance, None)

    def __set__(self, instance, value):
        self._values[instance] = value
