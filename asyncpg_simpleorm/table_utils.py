import inspect
import functools

from .abstract import AsyncModelABC
from .exceptions import InvalidModel


def _ensure_model(model):
    """Helper to test the input derives from :class:`AsyncModelABC`.

    :param model:  The input to check.

    """
    if inspect.isclass(model) and issubclass(model, AsyncModelABC):
        return model
    if isinstance(model, AsyncModelABC):
        return model
    raise InvalidModel(model)


def ensure_model(fn):
    """Decorator to ensure the first arg derives from :class:`AsyncModelABC`.

    """
    @functools.wraps(fn)
    def decorator(model, *args, **kwargs):
        return fn(_ensure_model(model), *args, **kwargs)

    return decorator


@ensure_model
async def drop_table(model, cascade=False) -> None:
    """Drop a database table.

    :param model:  An :class:`AsyncModelABC` subclass to drop the table for.
    :param cascade:  If ``True`` then we add the ``CASCADE`` clause to the
                     statement when executed.

    """
    tablename = model.tablename()
    stmt = f'DROP TABLE IF EXISTS {tablename}'
    if cascade is True:
        stmt += ' CASCADE'

    await model.execute(stmt)


@ensure_model
async def truncate_table(model, cascade: bool=False) -> None:
    """Truncate a table, leaving the table schema intact.

    :param model:  An :class:`AsyncModelABC` subclass to drop the table for.
    :param cascade:  If ``True`` then we add the ``CASCADE`` clause to the
                     statement when executed.

    """
    tablename = model.tablename()
    stmt = f'TRUNCATE TABLE {tablename}'
    if cascade is True:
        stmt += ' CASCADE'

    await model.execute(stmt)


@ensure_model
async def create_table(model) -> None:
    """Create a database table.

    :param model:  An :class:`AsyncModelABC` subclass to drop the table for.

    """
    cols = ', \n'.join(
        map(lambda col: col[1].pg_column_string, model._columns())
    )
    tablename = model.tablename()
    stmt = f'''
        CREATE TABLE IF NOT EXISTS {tablename} (
            {cols}
        )
    '''

    await model.execute(stmt)
