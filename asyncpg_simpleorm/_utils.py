import typing


def quote_if_string(val: typing.Any) -> typing.Any:
    if isinstance(val, str):
        return f"'{val}'"
    return val


def all_checks(Cls, *props) -> bool:
    """Helper for ``__subclasshook__`` methods.

    :param Cls:  The class to check for the attributes in it's ``__mro__``
    :param props:  Attribute names to ensure are in the ``Cls``.

    """
    checks = map(
        lambda x: any(x in vars(Base) for Base in Cls.__mro__),
        props
    )
    return all(checks)
