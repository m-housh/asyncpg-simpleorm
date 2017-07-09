import abc
import typing
from .._utils import all_checks


class ColumnTypeABC(metaclass=abc.ABCMeta):
    """Abstract representation of a postgres column type.

    """
    @property
    @abc.abstractmethod
    def pg_type_string(self) -> str:  # pragma: no cover
        """Return the postgres type string.

        """
        pass

    @abc.abstractmethod
    def __str__(self) -> str:  # pragma: no cover
        """This default implementation returns the ``pg_type_string``, and
        can be accessed via the ``super`` mechanism.

        """
        return self.pg_type_string

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is ColumnTypeABC:
            return all_checks(Cls, 'pg_type_string', '__str__')
        return NotImplemented  # pragma: no cover


class ColumnTypeMeta(type):
    """Ensures all ColumnType's declare ``__slots__``.  If a subclass does not
    have an ``__init__`` method, then this metaclass will add the ``__slots__``
    attribute.

    :raises RuntimeError:  If subclass has an ``__init__`` method and does
                           not declare ``__slots__``.

    """
    def __new__(cls, name, bases, namespace, **kwargs):
        if '__slots__' not in namespace:
            if '__init__' in namespace:
                raise RuntimeError(
                    f'{name} does not declare __slots__, but has __init__'
                )
            namespace['__slots__'] = ()
        return type.__new__(cls, name, bases, namespace, **kwargs)


class ColumnType(metaclass=ColumnTypeMeta):
    """Implementation of :class:`ColumnTypeABC`.

    """
    __slots__ = ()

    _pg_type_string: typing.ClassVar[str] = None

    @property
    def pg_type_string(self):
        return self._pg_type_string

    def __str__(self):
        return str(self.pg_type_string)

    def __init_subclass__(cls, pg_type_string=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if pg_type_string is None:
            raise RuntimeError(
                f'ColumnType subclass did not declare pg_type_string: {cls}'
            )
        cls._pg_type_string = str(pg_type_string)


class String(ColumnType, pg_type_string='text'):

    __slots__ = ('_n', )

    def __init__(self, n: int=None) -> None:
        self._n = int(n) if n is not None else None

    @property
    def pg_type_string(self) -> str:
        if self._n is not None:
            return f'varchar({self._n})'
        return 'text'


class UUID(ColumnType, pg_type_string='uuid'):
    pass


class Boolean(ColumnType, pg_type_string='bool'):
    pass


class Integer(ColumnType, pg_type_string='integer'):
    pass


class Number(ColumnType, pg_type_string='numeric'):
    pass


class Date(ColumnType, pg_type_string='date'):
    pass


class Time(ColumnType, pg_type_string='time'):
    pass


class TZTime(ColumnType, pg_type_string='time with timezone'):
    pass


class TimeStamp(ColumnType, pg_type_string='timestamp'):
    pass


class TZTimeStamp(ColumnType, pg_type_string='timestamp with timezone'):
    pass


class TimeInterval(ColumnType, pg_type_string='interval'):
    pass
