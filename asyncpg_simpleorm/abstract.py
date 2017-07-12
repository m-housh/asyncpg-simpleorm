import abc
import typing

from ._utils import all_checks


class AsyncModelABC(metaclass=abc.ABCMeta):
    """Abstract representation of an async database model.

    Ensures that an object declares, :meth:`column_names`, :meth:`tablename`,
    :meth:`connection`, :meth:`from_record`, :meth:`__init_subclass__` that
    allows a connection manager to be registered with subclasses.

    """

    @classmethod
    @abc.abstractmethod
    def column_names(cls) -> typing.Iterable[str]:  # pragma: no cover
        """Return the database column names.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def tablename(cls) -> str:  # pragma: no cover
        """Return the database table name.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def connection(cls) -> 'AsyncContextManagerABC':  # pragma: no cover
        """Return an async context manager, that returns an
        :class:`asyncpg.Connection` instance when used in an ``async with``
        block.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_record(cls, record):  # pragma: no cover
        """Return an instance of the class from an :class:`asyncpg.Record`
        instance.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def __init_subclass__(cls, connection=None, **kwargs):  # pragma: no cover
        """Allow a connection manager to be registered with a class in
        the class declaration.

        """
        pass

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is AsyncModelABC:
            return all_checks(Cls, 'connection', 'from_record',
                              '__init_subclass__', 'column_names', 'tablename')
        return NotImplemented  # pragma: no cover


class AsyncContextManagerABC(metaclass=abc.ABCMeta):
    """Abstract representation of an async context manager.

    Ensures a class has :meth:`__aenter__` and :meth:`__aexit__` methods.

    """
    @abc.abstractmethod
    async def __aenter__(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    async def __aexit__(self, exctype, excval, traceback):  # pragma: no cover
        pass

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is AsyncContextManagerABC:
            return all_checks(Cls, '__aenter__', '__aexit__')
        return NotImplemented  # pragma: no cover
