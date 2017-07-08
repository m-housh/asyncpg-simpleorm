class BaseException(Exception):
    """The base exception class.

    """
    pass


class ExecutionFailure(BaseException, ValueError):
    """Raised if execution of a database statement fails.

    """
    pass


class InvalidModel(BaseException, TypeError):
    """Raised if a model does not pass an ``issubclass`` or ``isinstance``
    check against :class:`ModelABC`.

    """
    pass
