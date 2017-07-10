import typing
import functools
import uuid
import inspect
from .._utils import quote_if_string

from .column_types import ColumnTypeABC, ColumnTypeMeta, ColumnType, String, \
    UUID, Boolean, Integer, Number, Date, Time, TZTime, TZTimeStamp, \
    TimeStamp, TimeInterval, Array, Bit, BigInteger, BigSerial, Binary, \
    FixedLengthString, Money, IPAddress, MACAddress, Box, Line, LineSegment, \
    Circle, Path, Point, Polygon, Double, Json, JsonB, PGLogSequenceNumber, \
    Real, SmallInteger, SmallSerial, Serial, TextSearchQuery, \
    TextSearchVector, TransactionID, XML

__all__ = (
    'Column',
    'ColumnTypeABC',
    'ColumnTypeMeta',
    'ColumnType',

    # column types
    'String',
    'UUID',
    'Boolean',
    'Integer',
    'Number',
    'Date',
    'Time',
    'TimeStamp',
    'TZTime',
    'TZTimeStamp',
    'TimeInterval',
    'Bit',
    'BigInteger',
    'Array',
    'BigSerial',
    'Binary',
    'FixedLengthString',
    'Money',
    'IPAddress',
    'MACAddress',
    'Box',
    'Line',
    'LineSegment',
    'Circle',
    'Path',
    'Point',
    'Polygon',
    'Double',
    'Json',
    'JsonB',
    'PGLogSequenceNumber',
    'Real',
    'SmallInteger',
    'SmallSerial',
    'Serial',
    'TextSearchQuery',
    'TextSearchVector',
    'TransactionID',
    'XML',
)


def _parse_column_input(fn):

    @functools.wraps(fn)
    def decorator(self, *args, **kwargs):
        kwargs.setdefault(
            'key',
            next((a for a in args if isinstance(a, str)), None)
        )
        kwargs.setdefault(
            '_type',
            next((a for a in args if inspect.isclass(a) and
                  issubclass(a, ColumnTypeABC) or isinstance(a, ColumnTypeABC)),
                 None)
        )
        return fn(self, **kwargs)

    return decorator


class Column:
    """A descriptor class that represents a table column.

    :param key:  The table column name in the database.  If not set, then this
                 will be set to the attribute name used on the
                 :class:`AsyncModel` subclass the column was declared on.
    :param type:  The :class:`ColumnType` subclass to use for the column.
    :param default:  A value or callable that is used for a default value.
                     If this is callable, then it should recieve no input and
                     return a value when called.
    :param primary_key:  Set's if the column is a primary key column.  Primary
                         key columns are used in certain query statements, such
                         as :meth:`AsyncModel.save`

    """
    __slots__ = ('key', 'default', 'primary_key', '_type', '_hidden_key')

    @_parse_column_input
    def __init__(self, key: str=None,
                 _type: typing.Union[ColumnType, typing.Type[ColumnType]]=None,
                 *, default: typing.Any=None, primary_key: bool=False):
        self.key = key
        self._type = _type
        self.default = default
        self.primary_key = primary_key
        self._hidden_key = '__' + uuid.uuid4().hex

    @property
    def pg_column_string(self) -> str:
        if self._type is None:
            raise TypeError('No _type set on column')
        else:
            if inspect.isclass(self._type):
                self._type = self._type()
            if not isinstance(self._type, ColumnTypeABC):
                raise TypeError('Invalid _type set on column: {self._type}')

        rv = f'{self.key} {self._type}'
        if self.primary_key is True:
            rv += ' PRIMARY KEY'
        return rv

    def __get__(self, instance, owner):
        if instance is None:
            # This gives access to attributes when accessed from the class
            # which a ``Column`` is delared on.
            return self
        # This is when trying to access the value of a ``Column`` from an
        # instance of the class which declared the ``Column``.
        #
        # check the instance for a value already set.
        rv = getattr(instance, self._hidden_key, None)
        # if a value hasn't been set, then we set it to the ``default``,
        # which can be a callable or a value.
        if rv is None:
            # set the value to the ``default`` or the value returned by
            # calling ``default``.
            rv = self.default() if callable(self.default) else self.default
            self.__set__(instance, rv)
        return rv

    def __set__(self, instance, value):
        # stores the value on the instance.
        setattr(instance, self._hidden_key, value)

    def __repr__(self):
        cn = self.__class__.__name__
        attrs = ', '.join(
            '{}={}'.format(attr, quote_if_string(getattr(self, attr)))
            for attr in self.__slots__ if not attr.startswith('_')
        )
        attrs += f', _type={self._type}'
        return f'{cn}({attrs})'
