import inspect
import typing

from .abstract import ColumnTypeABC
from .base_column_type import ColumnType


class String(ColumnType):
    """Representation of postgres string column.  Dependening on the context
    this will either produce a ``text`` column or ``varchar(n)`` column.

    :param n:  An optional integer for the length of the string.  If this is
               present then we use ``varchar(n)``, else we use ``text``.

    """

    def __init__(self, n: int=None) -> None:
        if n is not None:
            super().__init__(f'varchar({n})')
        else:
            super().__init__('text')


class FixedLengthString(ColumnType, pg_type_string='char'):
    """Representation of postgres ``char`` type.

    :param n: The number of characters.

    """

    def __init__(self, n: int):
        super().__init__(f'char({n})')


class Bit(ColumnType, pg_type_string='varbit'):
    """Representation of postgres ``bit`` or ``varbit`` type.

    :param n:  The number of bits.
    :param fixed_length:  An optional boolean.  If ``True`` we will use
                          ``bit(n)``. If ``False`` (default), we will use
                          ``varbit(n)``.

    """

    def __init__(self, n, fixed_length=False):
        n = int(n)
        if fixed_length:
            super().__init__(f'varbit({n})')
        else:
            super().__init__(f'bit({n})')


class UUID(ColumnType, pg_type_string='uuid'):
    """Representation of postgres ``uuid`` type.

    """

    pass


class Boolean(ColumnType, pg_type_string='bool'):
    """Representation of postgres ``bool`` type.

    """

    pass


class Integer(ColumnType, pg_type_string='integer'):
    """Representation of postgres ``integer`` type.

    """

    pass


class BigInteger(ColumnType, pg_type_string='int8'):
    """Representation of postgres ``int8`` type.

    """

    pass


class SmallInteger(ColumnType, pg_type_string='int2'):
    """Representation of postgres ``int2`` type.

    """

    pass


class Number(ColumnType, pg_type_string='numeric'):
    """Representation of postgres ``numeric`` type.

    """

    pass


class Double(ColumnType, pg_type_string='float8'):
    """Representation of postgres ``float8`` type.

    """

    pass


class Real(ColumnType, pg_type_string='float4'):
    """Representation of postgres ``float4`` type.

    """

    pass


class Serial(ColumnType, pg_type_string='serial4'):
    """Representation of postgres ``serial4`` type.

    """

    pass


class SmallSerial(ColumnType, pg_type_string='serial2'):
    """Representation of postgres ``serial2`` type.

    """

    pass


class BigSerial(ColumnType, pg_type_string='serial8'):
    """Representation of postgres ``serial8`` type.

    """

    pass


class Date(ColumnType, pg_type_string='date'):
    """Representation of postgres ``date`` type.

    """

    pass


class Time(ColumnType, pg_type_string='time'):
    """Representation of postgres ``time`` or ``timetz`` type.

    :param with_timezone:  If ``True`` then it is time with timezone.  If
                           ``False`` (default) then it time without timezone.

    """

    def __init__(self, with_timezone: bool=False):
        if with_timezone:
            super().__init__('timetz')
        else:
            super().__init__('time')


class Timestamp(ColumnType, pg_type_string='timestamp'):
    """Representation of postgres ``timestamp`` or ``timestamptz`` type.

    :param with_timezone:  If ``True`` then it is timestamp with timezone type.
                           If ``False`` (default) then it timestamp without
                           timezone type.

    """

    def __init__(self, with_timezone: bool=False):
        if with_timezone:
            super().__init__('timestamptz')
        else:
            super().__init__('timestamp')


class TimeInterval(ColumnType, pg_type_string='interval'):
    """Representation of postgres ``interval`` type.

    """

    pass


class Array(ColumnType, pg_type_string='ARRAY'):
    """Representation of postgres ``ARRAY`` type.

    :param _type:  The type of the elements in the array.  This would be another
                   :class:`ColumnType` subclass.
    :param n:  An optional ``int``, that will make a ``sized`` array.
    :param dimensions:  An optional ``int`` that will create a dimensional
                        array.

    Example::

        >>> Array(Integer()).pg_type_string
        integer ARRAY
        >>> Array(Integer(), 3).pg_type_string
        integer ARRAY[3]
        >>> Array(Integer(), 3, 3).pg_type_string
        integer [3][3][3]

    """

    def __init__(self, _type, n=None, dimensions=None):
        string = self._parse(
            self._parse_type(_type),
            n,
            dimensions
        )
        super().__init__(string)

    def _parse_type(self, val):
        if val:
            if inspect.isclass(val):
                val = val()

            if not isinstance(val, ColumnTypeABC):
                raise TypeError(val)
        return val

    def _parse(self, _type, n, dimensions) -> str:
        if n:
            n = int(n)

        if dimensions is not None:
            # create a dimensional (possibly) sized array.
            rv = f'{_type}'
            if not n:
                n = ''

            rv += ' ' + ''.join(
                map(lambda _: f'[{n}]', range(dimensions))
            )
            return rv
        # create a non-dimension (possibly sized) array.
        rv = f'{_type} ARRAY'
        if n:
            rv += f'[{n}]'
        return rv


class Binary(ColumnType, pg_type_string='bytea'):
    """Representation of postgres ``bytea`` type.

    """
    pass


class Money(ColumnType, pg_type_string='money'):
    """Representation of postgres ``money`` type.

    """

    pass


class IPAddress(ColumnType, pg_type_string='cidr'):
    """Representation of postgres ``cidr``  or ``inet`` types.

    :param inet:  An optional bool.  If ``True`` then we will use ``inet``.  If
                  ``False`` (default) then we use ``cidr``.

    """

    def __init__(self, inet=False):
        if inet:
            super().__init__('inet')
        else:
            super().__init__('cidr')


class MACAddress(ColumnType, pg_type_string='macaddr'):
    """Representation of postgres ``macaddr`` type.

    """

    pass


class Box(ColumnType, pg_type_string='box'):
    """Representation of postgres ``box`` type.

    """

    pass


class Line(ColumnType, pg_type_string='line'):
    """Representation of postgres ``line`` type.

    """

    pass


class LineSegment(ColumnType, pg_type_string='lseg'):
    """Representation of postgres ``lseg`` type.

    """

    pass


class Circle(ColumnType, pg_type_string='circle'):
    """Representation of postgres ``circle`` type.

    """

    pass


class Path(ColumnType, pg_type_string='path'):
    """Representation of postgres ``path`` type.

    """

    pass


class Point(ColumnType, pg_type_string='point'):
    """Representation of postgres ``point`` type.

    """

    pass


class Polygon(ColumnType, pg_type_string='polygon'):
    """Representation of postgres ``polygon`` type.

    """

    pass


class Json(ColumnType, pg_type_string='json'):
    """Representation of postgres ``json`` type.

    """

    pass


class JsonB(ColumnType, pg_type_string='jsonb'):
    """Representation of postgres ``jsonb`` type.

    This is not supported by all postgres versions.

    """

    pass


class PGLogSequenceNumber(ColumnType, pg_type_string='pg_lsn'):
    """Representation of postgres ``pg_lsn`` type.

    This is not supported by all postgres versions.

    """

    pass


class TextSearchQuery(ColumnType, pg_type_string='tsquery'):
    """Representation of postgres ``tsquery`` type.

    """

    pass


class TextSearchVector(ColumnType, pg_type_string='tsvector'):
    """Representation of postgres ``tsvector`` type.

    """

    pass


class TransactionID(ColumnType, pg_type_string='txid_snapshot'):
    """Representation of postgres ``txid_snapshot`` type.

    """

    pass


class XML(ColumnType, pg_type_string='xml'):
    """Representation of postgres ``xml`` type.

    """

    pass


class IntegerRange(ColumnType, pg_type_string='int4range'):
    """Representation of postgres ``int4range`` or ``int8range`` types.

    :param big:  A boolean if ``True`` then will represent an ``int8range``.
                 If ``False`` (default) then we will use ``int4range``.

    """

    def __init__(self, big=False):
        if big:
            super().__init__('int8range')
        else:
            super().__init__('int4range')


class NumericRange(ColumnType, pg_type_string='numrange'):
    """Representation of postgres ``numrange`` type.

    """

    pass


class DateRange(ColumnType, pg_type_string='daterange'):
    """Representation of postgres ``daterange`` type.

    """

    pass
