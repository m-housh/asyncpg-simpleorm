import abc
import typing


def _all_checks(Cls, *props) -> bool:
    """Helper for ``__subclasshook__`` methods.

    :param Cls:  The class to check for the attributes in it's ``__mro__``
    :param props:  Attribute names to ensure are in the ``Cls``.

    """
    checks = map(
        lambda x: any(x in vars(Base) for Base in Cls.__mro__),
        props
    )
    return all(checks)


class ModelABC(metaclass=abc.ABCMeta):
    """Abstract reperesentation of a database model.

    """
    @classmethod
    @abc.abstractmethod
    def column_names(cls) -> typing.Iterable[str]:  # pragma: no cover
        pass

    @classmethod
    @abc.abstractmethod
    def tablename(cls) -> str:  # pragma: no cover
        pass

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is ModelABC:
            return _all_checks(Cls, 'column_names', 'tablename')
        return NotImplemented  # pragma: no cover


class AsyncModelABC(metaclass=abc.ABCMeta):
    """Abstract representation of an async database model.

    """
    @classmethod
    @abc.abstractmethod
    def column_names(cls) -> typing.Iterable[str]:  # pragma: no cover
        pass

    @classmethod
    @abc.abstractmethod
    def tablename(cls) -> str:  # pragma: no cover
        pass

    @classmethod
    @abc.abstractmethod
    def connection(cls) -> 'AsyncContextManagerABC':  # pragma: no cover
        """Return an async context manager, that returns an
        :class:`asyncpg.Connection` instance.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_record(cls, record) -> 'AsyncModelABC':  # pragma: no cover
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
            return _all_checks(Cls, 'connection', 'from_record',
                               '__init_subclass__', 'column_names', 'tablename')
        return NotImplemented  # pragma: no cover


class AsyncContextManagerABC(metaclass=abc.ABCMeta):
    """Abstract representation of an async context manager.

    Ensures a class has ``__aenter__`` and ``__aexit__`` methods.

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
            return _all_checks(Cls, '__aenter__', '__aexit__')
        return NotImplemented  # pragma: no cover
