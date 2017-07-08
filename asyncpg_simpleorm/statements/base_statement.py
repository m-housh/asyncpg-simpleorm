import inspect
import typing

from ..abstract import ModelABC
from ..exceptions import InvalidModel
from .abstract import StatementABC, SimpleDescriptor


def counter(start=1):
    """Simple counter generator, used to keep track of query args.

    :param start:  The number to start out the counter with.

    """
    while True:
        yield start
        start += 1


def _safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except:
        pass


def _quote_if_str(val):
    if isinstance(val, str):
        return f"'{val}'"
    return val


class StatementDescriptor(SimpleDescriptor):
    """Specialized descriptor for use with the :class:`StatementValues` class.
    This will raise an error if another statement is already set on an instance.

    """
    __slots__ = SimpleDescriptor.__slots__

    def __set__(self, instance, value):
        # check if a statement is set on an instance and raise an error,
        # if so.
        if isinstance(instance, StatementValues) and \
                instance.get_statement() is not None:
            raise TypeError()
        self._values[instance] = value


class ClauseDescriptor(SimpleDescriptor):

    __slots__ = SimpleDescriptor.__slots__


class StatementValues:
    """Container that holds the values for a :class:`BaseStatement`.  This
    only allows a single statement to be set on an instance, avoiding errors
    with the argument count for the query args.

    """
    select = StatementDescriptor()
    insert = StatementDescriptor()
    update = StatementDescriptor()
    delete = StatementDescriptor()
    from_ = ClauseDescriptor()
    where = ClauseDescriptor()

    @classmethod
    def _get_descriptor(cls, descriptor) -> typing.Iterator[typing.Any]:
        """Returns the attribute names for the descriptor type.

        :param descriptor:  The descriptor type to use for an instance check.

        """
        return (
            k for (k, v) in vars(cls).items() if isinstance(v, descriptor)
        )

    @classmethod
    def clauses(cls):
        """Returns the attribute names for the :class:`ClauseDescriptor`'s

        """
        return tuple(cls._get_descriptor(ClauseDescriptor))

    @classmethod
    def statements(cls):
        """Returns the attribute names for the :class:`StatementDescriptor`'s

        """
        return tuple(cls._get_descriptor(StatementDescriptor))

    def get_statement(self, strict=False):
        """Return the current statement set on the instance.

        """
        for attr in self.statements():
            val = getattr(self, attr, None)
            if val:
                return val
        if strict is True:
            raise TypeError()

    def get_clauses(self):
        """Return any clauses set on an instance.

        """
        return tuple(getattr(self, x) for x in self.clauses())

    def query_string(self, sep='\n'):
        """Return a string that can be used in a database query.

        This combines the ``statements`` and ``clauses`` into a query.

        :param sep:  The seperator to use to combine the statement and clauses.
                     Defaults to '\\n'.

        :raises TypeError: If a statement has not yet been set on an instance.

        """
        stmt = self.get_statement(strict=True)[0]
        vals = [stmt] + [c[0] for c in self.get_clauses() if c is not None]
        return sep.join(vals)

    def _query_args(self):
        """Flatten's all the args set on an instance.

        """
        stmt = self.get_statement()
        if stmt and stmt[1]:
            for arg in stmt[1]:
                yield arg

        for clause in self.get_clauses():
            if clause and clause[1]:
                for arg in clause[1]:
                    yield arg

    def query_args(self):
        """Returns the query arguments set on the instance.

        """
        return tuple(self._query_args())

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __iter__(self):
        return iter((self.query_string(), ) + self.query_args())

    def __str__(self):
        try:
            return self.query_string()
        except:
            return ''

    def __repr__(self):
        cn = self.__class__.__name__
        query_string = _quote_if_str(
            _safe_call(self.query_string)
        )
        args = self.query_args()
        return f'{cn}({query_string}, {args})'


class BaseStatement(StatementABC):
    """Implementation of the :class:`StatementABC`.


    """

    __slots__ = ('_values', '_model', 'kwargs', 'count')

    def __init__(self, model, kwargs={}, arg_count: int=1):
        self.model = model
        self.count = counter(arg_count)
        self.kwargs = kwargs
        self._values = StatementValues()

    @property
    def model(self):
        """Return the database model set on an instance.  And ensures that
        the model is derived from :class:`ModelABC`.

        :raises ..exceptions.InvalidModel:  If trying to set an invalid model
                                            on an instance.

        """
        return getattr(self, '_model', None)

    @model.setter
    def model(self, model):
        if model:
            if inspect.isclass(model) and not issubclass(model, ModelABC):
                raise InvalidModel(model)
            elif not inspect.isclass(model) and not isinstance(model, ModelABC):
                raise InvalidModel(model)
        self._model = model

    def set_statement(self, key: str, query_string: str,
                      args: typing.Tuple[typing.Any]=None) -> 'BaseStatement':
        """Set the statement for an instance, and return ``self`` for method
        chaining.

        """
        if query_string:
            self._values[key] = (query_string, args or ())
        return self

    def set_count(self, count: int) -> None:
        """Reset's the counter for an instance.

        :param count:  The number to reset the counter to.

        """
        self.count = counter(count)

    def query_string(self, sep='\n') -> str:
        """Get the query string set on the instance.

        :param sep:  A seperator used to join the statement and the clauses.
                     Defaults to '\\n'.
        :raises TypeError: If a statement has not yet been set on an instance.

        """
        return self._values.query_string(sep)

    def query_args(self) -> typing.Iterable[typing.Any]:
        """Get the query args set on the instance.  This will return an empty
        tuple if no args have been set on the instance yet.

        If args are set on the instance, then they will be returned in the
        order corresponding to their place holder in the ``query_string``.

        """
        return self._values.query_args()

    def _column_string(self, tablename=False) -> str:
        """Helper that joins the column names of the ``model`` set on the
        instance.  Optionally with the ``tablename.column_name`` syntax.

        :param tablename:  A bool that tells whether to use the tablename syntax
                           or just the column names.

        """
        cols = self.model.column_names()
        if tablename:
            tablename = self.model.tablename()
            return ', '.join(map(lambda x: f'{tablename}.{x}', cols))
        return ', '.join(cols)

    def query(self):
        """Returns the representation of the query set on the instance.

        """
        return tuple(self._values)

    def __iter__(self):
        # allows a statement to be passed in to an asyncpg.fetch (etc.) using
        # as a *args.
        return iter(self._values)

    def __str__(self):
        # return the query string.
        return str(self._values)

    def __repr__(self):
        cn = self.__class__.__name__
        model = self.model
        stmt = _quote_if_str(str(self._values))
        return f"{cn}(statement={stmt}, model={model})"
