import inspect
import typing
import functools
from .base_statement import BaseStatement
from .abstract import StatementABC

__all__ = (
    'BaseStatement',
    'StatementABC',
    'Statement',
    'select',
    'update',
    'insert',
    'delete'
)

ItemsType = typing.Iterable[typing.Tuple[str, typing.Any]]


def _callback(callback, *args, **kwargs):
    """Helper that marks a method to call another method on the
    same class when complete.

    :param callback:  The method name to call when the marked method is complete
    :param args:  Saved and passed to the callback method.
    :param kwargs:  Saved and passed to the callback method.

    :raises TypeError:  If the callback is not found or is not callable.

    """
    def decorator(fn):

        @functools.wraps(fn)
        def decorated(self, *_args, **_kwargs):
            _callback = getattr(self, callback, None)
            if not _callback or not callable(_callback):
                raise TypeError(f'Invalid callback: {callback}')
            fn(self, *_args, **_kwargs)
            return _callback(*args, **kwargs)

        return decorated

    return decorator


class _reset_counter:
    """Mark a method to reset the counter when marked.

    :param stmt:  A string to use to split/search for the counter int.

    """
    __slots__ = ('_stmt', )

    def __init__(self, stmt: str):
        self._stmt = stmt

    def _find_ints(self, string: str) -> typing.Generator[int, None, None]:
        """Helper to parse and find the integers in a query string after the
        ``stmt`` in a string.

        Searches for substrings similar to ['$1', '$2', ...'$n']

        :param string:  The full string to search for the int in.

        """
        if self._stmt in string:
            split_strings = iter(string.split(self._stmt)[1].split('$'))
            for s in split_strings:
                try:
                    yield int(s)
                except ValueError:
                    pass

    def __call__(self, fn):

        @functools.wraps(fn)
        def decorator(instance, *args, **kwargs):
            if isinstance(instance, StatementABC):
                count = next(self._find_ints(instance.query_string()), None)
                if count is not None:
                    instance.set_count(count)

            return fn(instance, *args, **kwargs)

        return decorator


class Statement(BaseStatement):
    """Extends the :class:`BaseStatement` class.  This class is normally not
    instantiated directly, but returned from one of the statement factory
    functions.

    """

    __slots__ = BaseStatement.__slots__

    def _get_column(self, col: str):
        """Retrieve the column value from the model set on the instance.

        :param col:  The column name to get.

        """
        col = self.model.attr_name_for_column(col)
        return getattr(self.model, col, None)

    def _get_args_from_model(self):
        """Returns the values of all the columns for the model set on the
        instance. Replacing any ``None`` values with ``'NULL'``.

        :raises TypeError: If no model is set or the model is a ``class`` not an
                           instance.

        """
        if not self.model or inspect.isclass(self.model):
            raise TypeError(self.model)
        return tuple(self._get_column(col) for col in self.model.column_names())

    def _get_args_from_kwargs(self):
        """Returns the values of the kwargs set on the instance.

        :raises TypeError: If no kwargs are set on the instance.

        """
        if not self.kwargs:
            raise TypeError(self.kwargs)
        return tuple(
            self.kwargs.get(col, self.kwargs.get(
                            self.model.attr_name_for_column(col)))
            for col in self.model.column_names()
        )

    def _get_args(self):
        """Get the values to be used as ``args`` for the statement.  We try
        to get them from the ``model`` set on the instance, if that fails then
        we try to get them from the ``kwargs`` set on the instance.

        :raises TypeError:  If failed to get args from the ``model`` or
                            ``kwargs``

        """
        try:
            return self._get_args_from_model()
        except TypeError:
            return self._get_args_from_kwargs()

    def _parse_where_items(self,
                           items: ItemsType,
                           check: typing.Iterable[str]=None,
                           strict_check: bool=False
                           ) -> typing.Tuple[str, typing.Tuple[typing.Any]]:
        """Iterates through the items, building a partial string for use in
        the ``where`` statement.

        :param items:  The items to iterate through.  They should be an iterable
                       of (key, value) pairs.
        :param check:  An iterable of strings to verify that the key is
                       acceptable
        :param strict_check:  If ``True`` then raise errors if the key is not
                              in the ``check`` iterable.

        :raises ValueError:  If the key is not in the ``check`` iterable.
        :raises TypeError:  If no items were parsed.

        """
        tablename = self.model.tablename()
        strings = []
        args = []
        for key, value in items:
            try:
                key = self.model.ensured_column_name(key)
            except ValueError:
                pass
            # verify the key is in the ``check`` if applicable.
            if value and check is None or key in check:
                # passed verification, so we store create a query string
                # and save the value.
                count = next(self.count)
                strings.append(f'{tablename}.{key} = ${count}')
                args.append(value)
            # raise errors if the key is not valid and the caller wants
            # errors to be raised
            elif strict_check is True and check is not None:
                raise ValueError(key)

        if not len(strings) > 0:
            # we didn't find anything, so raise an error.
            raise TypeError()

        # return the partial ``where`` string and args.
        return ' AND'.join(strings), tuple(args)

    def _parse_where(self, primary_keys=False):
        """Parses the ``model`` or ``kwargs`` set on an instance and builds
        a partial string and the query args for the ``where`` statement.

        :param primary_keys:  If ``True`` then only use the model's primary_keys
                              to parse the statement.

        :raises ValueError:  If not using the primary keys and the ``kwargs``
                             set on the instance include an invalid key.
        :raises TypeError:  If nothing was able to be parsed.

        """
        # default if parsing ``kwargs`` without primary keys.
        strict_check = True

        if primary_keys is True:
            check = self.model.primary_keys()
            strict_check = False
        else:
            check = self.model.column_names()

        if self.kwargs:
            return self._parse_where_items(
                self.kwargs.items(),
                check,
                strict_check=strict_check
            )
        elif not inspect.isclass(self.model):
            # model instances always uses, the primary keys.
            return self._parse_where_items(
                ((col, self._get_column(col)) for col
                 in self.model.primary_keys())
            )

        raise TypeError()

    def from_(self):
        """Add's the ``FROM`` clause string to the statement.

        """
        tablename = self.model.tablename()
        return self.set_statement('from_', f'FROM {tablename}')

    @_callback('from_')
    def select(self):
        """Set's the statement as a ``SELECT`` statement.

        """
        colstring = self._column_string(tablename=True)
        return self.set_statement('select', f'SELECT {colstring}')

    def insert(self, **kwargs):
        """Set's the statement as an ``INSERT`` statement.

        :param kwargs:  Values to use as (column names, query args) for the
                        statement.  These are probably not used much as you
                        should normally just set the model to an instance of
                        :class:`ModelABC` for the column names and values.

        """
        if kwargs:
            self.kwargs = kwargs

        args = self._get_args()
        tablename = self.model.tablename()
        colstring = self._column_string()
        values = ', '.join(
            map(lambda _: '${}'.format(next(self.count)), range(len(args)))
        )
        return self.set_statement(
            'insert',
            f'INSERT INTO {tablename} ({colstring}) VALUES ({values})',
            args
        )

    @_reset_counter('WHERE')
    def where(self, primary_keys=False, safe_call=False, **kwargs):
        """Add's the ``where`` string to the statement.

        :param primary_keys:  If ``True``, only parse primary keys for the
                              ``where`` string and args.  This is primarily an
                              implementation detail used in conjunction with
                              other statement callbacks, and typically not
                              necessarily set by a caller.
        :param safe_call:  An optional boolean to suppress errors. Default is
                           ``False``.
        :param kwargs:  An optional mapping of column names and values to use
                        for the where statement.

        :raises ValueError:  If not using the primary keys and the ``kwargs``
                             set on the instance include an invalid key.
        :raises TypeError:  If nothing was able to be parsed.

        """
        try:
            if kwargs:
                self.kwargs = kwargs
            where_str, args = self._parse_where(primary_keys=primary_keys)
            return self.set_statement('where', f'WHERE {where_str}', args)
        except (TypeError, ValueError) as exc:
            if safe_call is False:
                raise

        return self

    @_callback('where', primary_keys=True)
    def update(self, **kwargs):
        """Set's the statement as an ``UPDATE`` statement.  This will
        automatically set a ``where`` statement, using the primary keys.

        :param kwargs:  Values to use as column names, query args for the
                        statement.  These are probably not used much as you
                        should normally just set the model to an instance of
                        :class:`ModelABC` for the column names and values.

        :raises TypeError:  If no args were able to be parsed for the statement.

        """
        if kwargs:
            self.kwargs = kwargs

        args = self._get_args()
        colstring = self._column_string()
        tablename = self.model.tablename()
        arg_string = ', '.join(
            map(lambda _: '${}'.format(next(self.count)), range(len(args)))
        )
        return self.set_statement(
            'update',
            f'UPDATE {tablename} SET ({colstring}) = ({arg_string})',
            args
        )

    @_callback('where', primary_keys=True, safe_call=True)
    def delete(self):
        """Set's the statement as a ``DELETE`` statement.  This will
        automatically set a ``where`` statement, using the primary keys.

        """
        tablename = self.model.tablename()
        return self.set_statement(
            'delete',
            f'DELETE FROM {tablename}'
        )


def select(model):
    """Select statement factory.

    :param model:  A :class:`ModelABC` subclass to create the statement for.

    """
    return Statement(model).select()


def insert(model=None, **kwargs):
    """Insert statement factory.

    :param model:  A :class:`ModelABC` subclass instance to create the statement
                   for.
    :param kwargs:  Used for instance values, if the statement is created with
                    a class, not an instance.

    """
    return Statement(model, kwargs).insert()


def update(model=None, **kwargs):
    """Update statement factory.

    :param model:  A :class:`ModelABC` subclass instance to create the statement
                   for.
    :param kwargs:  Used for instance values, if the statement is created with
                    a class, not an instance.

    """
    return Statement(model, kwargs).update()


def delete(model, **kwargs):
    """Delete statement factory.

    :param model:  A :class:`ModelABC` subclass instance to create the statement
                   for.
    :param kwargs:  Used for instance values, if the statement is created with
                    a class, not an instance.
    """

    return Statement(model, kwargs).delete()
