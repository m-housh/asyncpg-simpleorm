import abc

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
