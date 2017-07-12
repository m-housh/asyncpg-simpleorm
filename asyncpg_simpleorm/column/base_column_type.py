import typing


class ColumnTypeMeta(type):
    """Ensures all ColumnType's declare ``__slots__``.  If a subclass does not
    have an ``__init__`` method, then this metaclass will add the ``__slots__``
    attribute.

    :raises RuntimeError:  If subclass has an ``__init__`` method and does
                           not declare ``__slots__``.

    """
    def __new__(cls, name, bases, namespace, **kwargs):
        if '__slots__' not in namespace:
            namespace['__slots__'] = ColumnType.__slots__
        return type.__new__(cls, name, bases, namespace, **kwargs)


class ColumnType(metaclass=ColumnTypeMeta):
    """Implementation of :class:`ColumnTypeABC`.

    This can be used as a generic column type, by passing a string into
    the constructor.  That string will be used, else we will use a value that's
    passed into the class declaration at ``pg_type_string``.

    :param string:  An optional input string that will be used for the column
                    type.  This string is not checked or validated, so if it's
                    not valid errors will bubble up when trying to create the
                    table.

    **Examples:**

    .. code-block:: python

        >>> str(ColumnType('text'))
        'text'
        >>> class Text(ColumnType, pg_type_string='text'): pass
        >>> str(Text())
        'text'

    Custom subclasses should implement ``__slots__``.  If they don't need to
    set any attributes on the class (which is typically the case) and they
    derive from ``ColumnType`` then the ``__slots__`` will be automatically
    added to the subclass.

    """

    __slots__ = ('_string', )

    _pg_type_string: typing.ClassVar[str] = None

    def __init__(self, string: str=None):
        self._string = string

    @property
    def pg_type_string(self) -> str:
        """Return's the postgres column type string for an instance.


        :raises TypeError: If neither an input string was passed in or
                           ``pg_type_string`` in the class declaration.

        """
        if self._string:
            return str(self._string)
        elif self._pg_type_string:
            return str(self._pg_type_string)
        # TODO: make a better error
        raise TypeError()

    def __str__(self):
        return str(self.pg_type_string)

    def __init_subclass__(cls, pg_type_string=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if pg_type_string:
            cls._pg_type_string = str(pg_type_string)

    def __repr__(self) -> str:
        cn = self.__class__.__name__
        return f"{cn}('{self.pg_type_string}')"
