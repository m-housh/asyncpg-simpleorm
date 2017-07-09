import abc
import inspect
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


class TZTime(ColumnType, pg_type_string='timetz'):
    pass


class TimeStamp(ColumnType, pg_type_string='timestamp'):
    pass


class TZTimeStamp(ColumnType, pg_type_string='timestamptz'):
    pass


class TimeInterval(ColumnType, pg_type_string='interval'):
    pass


class Array(ColumnType, pg_type_string='ARRAY'):

    __slots__ = ('_n', '__type', '_dimensions')

    def __init__(self, type, n=None, dimensions=None):
        self._type = type
        self._n = int(n) if n else None
        self._dimensions = int(dimensions) if dimensions else None

    @property
    def _type(self) -> typing.Optional[ColumnType]:
        return self.__type

    @_type.setter
    def _type(self, val):
        if val:
            if inspect.isclass(val):
                val = val()

            if not isinstance(val, ColumnTypeABC):
                raise TypeError(val)
        self.__type = val

    @property
    def pg_type_string(self) -> str:
        if self._dimensions is not None:
            # create a dimensional (possibly) sized array.
            rv = f'{self._type}'
            if self._n:
                n = self._n
            else:
                n = ''
            rv += ' ' + ''.join(
                map(lambda _: f'[{n}]', range(self._dimensions))
            )
            return rv
        # create a non-dimension (possibly sized) array.
        rv = f'{self._type} ARRAY'
        if self._n:
            rv += f'[{self._n}]'
        return rv


class BigInteger(ColumnType, pg_type_string='int8'):
    pass


class Bit(ColumnType, pg_type_string='varbit'):

    __slots__ = ('_n', '_fixed_length')

    def __init__(self, n, fixed_length=False):
        self._n = int(n)
        self._fixed_length = fixed_length

    @property
    def pg_type_string(self) -> str:
        if self._fixed_length:
            return f'bit({self._n})'
        return f'varbit({self._n})'


class BigSerial(ColumnType, pg_type_string='serial8'):
    pass


class Binary(ColumnType, pg_type_string='bytea'):
    pass


class FixedLengthString(ColumnType, pg_type_string='char'):

    __slots__ = ('_n', )

    def __init__(self, n: int):
        self._n = int(n)

    @property
    def pg_type_string(self) -> str:
        return f'char({self._n})'


class Money(ColumnType, pg_type_string='money'):
    pass


class IPAddress(ColumnType, pg_type_string='cidr'):

    __slots__ = ('_inet', )

    def __init__(self, inet=False):
        self._inet = inet

    @property
    def pg_type_string(self) -> str:
        if self._inet is True:
            return 'inet'
        return 'cidr'


class MACAddress(ColumnType, pg_type_string='macaddr'):
    pass


class Box(ColumnType, pg_type_string='box'):
    pass


class Line(ColumnType, pg_type_string='line'):
    pass


class LineSegment(ColumnType, pg_type_string='lseg'):
    pass


class Circle(ColumnType, pg_type_string='circle'):
    pass


class Path(ColumnType, pg_type_string='path'):
    pass


class Point(ColumnType, pg_type_string='point'):
    pass


class Polygon(ColumnType, pg_type_string='polygon'):
    pass


class Double(ColumnType, pg_type_string='float8'):
    pass


class Json(ColumnType, pg_type_string='json'):
    pass


class JsonB(ColumnType, pg_type_string='jsonb'):
    pass


class PGLogSequenceNumber(ColumnType, pg_type_string='pg_lsn'):
    pass


class Real(ColumnType, pg_type_string='float4'):
    pass


class SmallInteger(ColumnType, pg_type_string='int2'):
    pass


class SmallSerial(ColumnType, pg_type_string='serial2'):
    pass


class Serial(ColumnType, pg_type_string='serial4'):
    pass


class TextSearchQuery(ColumnType, pg_type_string='tsquery'):
    pass


class TextSearchVector(ColumnType, pg_type_string='tsvector'):
    pass


class TransactionID(ColumnType, pg_type_string='txid_snapshot'):
    pass


class XML(ColumnType, pg_type_string='xml'):
    pass
