import typing
import asyncpg
from .abstract import AsyncContextManagerABC
from .connection_managers import ConnectionManager, PoolManager
from .exceptions import ExecutionFailure
from .statements import select, delete, update, insert
from .column import Column
from ._utils import quote_if_string as _quote_if_str


# TODO:  Update metaclass for usage with __slots__
class ModelMeta(type):
    """Meta class for ``BaseModel``, which ensures the column's keys
    for the model are set, or will default to the attribute name a ``Column``
    was declared for.

    This allows the ``key`` attribute of a ``Column`` to be optional.

    Example::

        >>> class User(BaseModel):
                id = Column('_id', primary_key=True)
                name = Column()

        >>> User.id.key
        '_id'
        >>> User.name.key
        'name'

    """
    def __new__(cls, name, bases, namespace, **kwargs):

        # get any columns from the bases and set them in the
        # namespace.
        for base in bases:
            base_dic = vars(base)
            for key, val in base_dic.items():
                if isinstance(val, Column) and key not in namespace:
                    namespace[key] = val

        for key, value in namespace.items():
            if isinstance(value, Column) and value.key is None:
                value.key = key

        return type.__new__(cls, name, bases, namespace, **kwargs)


class BaseModel(metaclass=ModelMeta):
    """Base class for :class:`AsyncModel`. This class should typically not be
    used directly, unless building a custom statement generating class.

    This class allows column instance values to be set either by the attribute
    name the column was declared as, or the database column name (which are not
    always the same).

    Example::

        >>> class User(BaseModel):
                id = Column('_id', primary_key=True)
                name = Column()

        >>> u1 = User(id=123, name='foo')
        >>> u2 = User(_id=456, name='bar')
        >>> print(u1.id, u2.id)
        (123, 456)

    :param kwargs:  Key word args that are set on an instance.  These would
                    typically be the same ``keys`` as the declared
                    :class:`Column`'s on a subclass.

    """
    __tablename__: typing.ClassVar[str] = None
    """Set the database table name for the class.  If not set, then we will
    default to the lowercase version of the class name.

    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def _columns(cls) -> typing.Iterator[typing.Tuple[str, Column]]:
        """Iterator over the :class:`Column`'s set on the class.  This yields
        a tuple of the (attribute name, Column).

        Example::

            >>> class User(BaseModel):
                    id = Column('_id', primary_key=True)
                    name = Column()
            >>> list(User._columns())
            [('id', Column(...)), ('name', Column(...))]


        """
        for (k, v) in vars(cls).items():
            if isinstance(v, Column):
                yield (k, v)

    @classmethod
    def attr_name_for_column(cls, column_name: str) -> str:
        """Get the class attribute name for a given database column name.

        This is used when setting instance values for :class:`Column`'s, and
        allows access to the attribute name, whether the ``column_name`` was
        parsed using the actual database column name, or the attribute name
        (which can be different depending on the :class:`Column`).

        :param column_name:  The database column name to get the attribute name
                             for.
        :raises ValueError:  If no :class:`Column` is found for that column
                             name.

        Example::

            >>> class User(BaseModel):
                    id = Column('_id', primary_key=True)
                    name = Column()

            >>> User.attr_name_for_column('_id')
            'id'
            >>> User.attr_name_for_column('id')
            'id'



        """
        for attr_name, col in cls._columns():
            if col.key == column_name:
                return attr_name
            elif attr_name == column_name:
                return column_name
        raise ValueError(column_name)

    @classmethod
    def ensured_column_name(cls, attr_name: str) -> str:
        """This is helper to always return the database column name for the
        input.

        This is essentially the opposite of :meth:`attr_name_for_column`.

        :param column_name:  The attribute name to get the column name
                             for.
        :raises ValueError:  If no :class:`Column` is found for that attribute
                             name.

        Example::

            >>> class User(BaseModel):
                    id = Column('_id', primary_key=True)
                    name = Column()

            >>> User.ensured_column_name('_id')
            '_id'
            >>> User.ensured_column_name('id')
            '_id'


        """
        for attr, col in cls._columns():
            if attr_name == col.key:
                return attr_name
            elif attr_name == attr:
                return col.key
        raise ValueError(attr_name)

    @classmethod
    def column_names(cls) -> typing.Tuple[str]:
        """Returns a tuple of the column names for the class.

        """
        return tuple(c.key for (_, c) in cls._columns())

    @classmethod
    def tablename(cls):
        """Returns the tablename set for the class, if one is not set, then
        we default to the lowercase version of the class name + 's'.

        """
        if cls.__tablename__ is not None:
            return cls.__tablename__
        return cls.__name__.lower() + 's'

    @classmethod
    def primary_keys(cls) -> typing.Tuple[str]:
        """Returns a tuple of column names that are also primary keys.

        """
        return tuple(c.key for (_, c) in cls._columns()
                     if c.primary_key is True)

    def __setattr__(self, key, value):
        # check if the key is actually a database column name, and set the
        # appropriate key.
        try:
            key = self.attr_name_for_column(key)
        except ValueError:
            pass
        return super().__setattr__(key, value)

    def __repr__(self):
        cn = self.__class__.__name__
        attrs = tuple(
            map(self.attr_name_for_column, self.column_names())
        )
        attrs += tuple(k for k in vars(self).keys() if not k.startswith('_'))
        attr_string = ', '.join(
            map(lambda x: '{}={}'.format(x, _quote_if_str(getattr(self, x))),
                attrs)
        )
        return f'{cn}({attr_string})'


# TODO:  Update the ``delete`` method to be a classmethod, that accepts kwargs
class AsyncModel(BaseModel):
    """Extends the :class:`BaseModel` class to include helpful database
    queries.  Implements the :class:`AsyncModelABC` interface.

    By default :meth:`get` and :meth:`get_one` methods return
    :class:`asyncpg.Record` instances.  This option can be toggled class wide,
    by setting a class attribute :attr:`return_records` to ``False`` on a
    subclass, or can be toggled during a single method call

    .. seealso:: :meth:`get` and :meth:`get_one` methods for details.

    This class uses the :meth:`__init_subclass__` syntax new in ``python-3.6``.
    That allows ``kwargs`` to be passed into the class declaration.

    A user should subclass this providing a :class:`ConnectionManager` or
    :class:`PoolManager` to provide the database connection.

    :raises RuntimeError:  If subclass does not provide a ``connection`` kwarg
                           in the class declaration.

    **Example:**

    .. code-block:: python

        '''
        The following example would be for a postgres table created by.

        CREATE TABLE users (
          _id uuid PRIMARY KEY,
          name varchar(100) NOT NULL
        )
        '''

        import uuid

        DBURI = 'postgres://user:password@localhost:5432/database'

        class User(AsyncModel, connection=ConnectionManager(DBURI)):
            __tablename__ = 'users'

            id = Column('_id', primary_key=True, default=uuid.uuid4)
            name = Column()

        # Or using a ``PoolManager``.
        class User(AsyncModel, connection=PoolManager(DBURI)):
            ...


        # Create an instance using ``kwargs``
        user = User(name='foo')

        print(user)
        # User(id=95ccbcd3-2ded-4ad8-9f68-d60f0b9590a9, name='foo')

    """

    return_records: typing.ClassVar[bool] = True
    """Set whether to return :class:`asyncpg.Record` instances from ``get``
    queries.  Default is ``True``, set to ``False`` to always return instances
    of your subclass.

    """

    @classmethod
    def connection(cls) -> typing.Union[ConnectionManager, PoolManager]:
        """Obtain the connection manager that was registered with the
        subclass during creation.

        This is typically used with ``async with`` to gain access to an
        :class:`asyncpg.Connection` instance.

        **Example:**

        .. code-block:: python

            >>> async with User.connection() as conn:
                    # do something with the connection.

        """
        return cls._connection

    async def save(self) -> None:
        """Update or insert an instance to the database.

        :raises .exceptions.ExecutionFailure: If no records were updated or
                                              saved to the database.

        **Example:**

        .. code-block:: python

            >>> user = User(name='foo')
            >>> await user.save()


        """
        # try an update first. If nothing is updated then the
        # update_result will be 'UPDATE 0'.
        result = await self.execute(*update(self))
        if result == 'UPDATE 0':
            # if the update failed, then we try an insert
            # statement, and let any errors bubble up.
            # if the insert was successful, then the res_string
            # will be 'INSERT 0 1'.
            result = await self.execute(*insert(self))

        # check the result string, it should end with a '1' if any records
        # were updated/saved to the database.
        if not result[-1] == '1':  # pragma: no cover
            raise ExecutionFailure(f'Failed to insert or update: {self}')

    async def delete(self) -> None:
        """Delete an instance from the database.

        :raises .exceptions.ExecutionFailure:  If no records were deleted from
                                               the database.

        """
        result = await self.execute(*delete(self))

        # If the statement was successful, then the return value will
        # be 'DELETE 1'
        if not result[-1] == '1':
            raise ExecutionFailure(f'Failed to delete: {self}')

    @classmethod
    def _parse_records(cls, records: typing.Optional[bool]) -> bool:
        """Check if the input is ``None``, if it is then we return the value
        of the ``return_records`` attribute on the class.

        :param records:  The input value to check.

        """
        if records is None:
            return cls.return_records
        return records

    @classmethod
    async def get(cls, records: bool=None, **kwargs
                  ) -> typing.Iterable[typing.Any]:
        """Get a list of the table items from the database.

        :param records:  Optional bool. If ``True`` then we return
                         :class:`asyncpg.Record`'s. If ``False`` then we will
                         return instances of the ``AsyncModel`` subclass.  If
                         ``None``, then we default to what's set on the subclass
                         at the `return_records` attribute
                         (default is ``True``).
        :param kwargs:  Optional kwargs that are passed into a ``where`` clause.


        **Example:**

        .. code-block:: python

            >>> await User.get(records=False)
            [User(id=95ccbcd3-2ded-4ad8-9f68-d60f0b9590a9, name='foo'), ...]

            >>> await User.get()
            [<Record(_id=UUID('95ccbcd3-2ded-4ad8-9f68-d60f0b9590a9'),
            name='foo'>, ...]

        """
        # parse whether to return records or not.
        records = cls._parse_records(records)

        async with cls.connection() as conn:
            async with conn.transaction():
                stmt = select(cls)
                # set a where clause on the statement, if kwargs were passed in.
                if kwargs:
                    stmt.where(**kwargs)
                # fetch the results from the database.
                res = await conn.fetch(*stmt)
                if records is False:
                    # return instances of the class if that's what the caller
                    # wants.
                    return list(map(cls.from_record, res))
                # return the results as asyncpg.Record's
                return res

    @classmethod
    async def get_one(cls, record: bool=None, **kwargs) -> typing.Any:
        """Get a single item from the database.

        :param record:  Optional bool. If ``True`` then we return
                        :class:`asyncpg.Record`'s. If ``False`` then we will
                        return instances of the ``AsyncModel`` subclass.  If
                        ``None``, then we default to what's set on the subclass
                        at the `return_records` attribute
                        (default is ``True``).
        :param kwargs:  Optional kwargs that are passed into a ``where`` clause.

        **Example:**

        .. code-block:: python

            >>> await User.get_one(name='foo')
            <Record _id=UUID('95ccbcd3-2ded-4ad8-9f68-d60f0b9590a9'),
            name='foo'>
            >>> await User.get_one(record=False, name='foo')
            User(id=456, name='bar')

        """
        # parse whether to return records or not.
        record = cls._parse_records(record)

        async with cls.connection() as conn:
            async with conn.transaction():
                stmt = select(cls)
                # set a where clause on the statement, if kwargs were passed
                # in.
                if kwargs:
                    stmt.where(**kwargs)
                # get the result from the database.
                res = await conn.fetchrow(*stmt)

                if record is False:
                    # return instances of the class, not records
                    return cls.from_record(res)
                # return instances of the asyncpg record class
                return res

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> typing.Any:
        """Return an instance of the class from an :class:`asyncpg.Record`
        object.

        :param record:  An :class:`asyncpg.Record` instance to create a
                        database model instance from.

        """
        if record:
            return cls(**record)

    @classmethod
    async def execute(cls, *args, **kwargs):
        """Execute's a database query inside a transaction block.  This
        cuts down on the boiler plate nested ``async with`` statements to
        execute a query.

        This is equivalent to::

            >>> async with Model.connection() as conn:
            ...     async with conn.transaction():
            ...         return await conn.execute(*args, **kwargs)

        """
        async with cls.connection() as conn:
            async with conn.transaction():
                return await conn.execute(*args, **kwargs)

    @classmethod
    def __init_subclass__(cls, connection=None, **kwargs):
        super().__init_subclass__(**kwargs)

        err = False

        if connection is not None:
            if not isinstance(connection, AsyncContextManagerABC):
                err = True
            else:
                cls._connection = connection

        if err is True or not hasattr(cls, '_connection'):
            raise RuntimeError(
                (f'connection should be an asyncpg.Connection')
            )
