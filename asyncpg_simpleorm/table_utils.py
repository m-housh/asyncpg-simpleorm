import inspect
import functools

from .abstract import AsyncModelABC
from .exceptions import InvalidModel


def _ensure_model(model):
    if inspect.isclass(model) and issubclass(model, AsyncModelABC):
        return model
    if isinstance(model, AsyncModelABC):
        return model
    raise InvalidModel(model)


def ensure_model(fn):

    @functools.wraps(fn)
    def decorator(model, *args, **kwargs):
        return fn(_ensure_model(model), *args, **kwargs)

    return decorator


@ensure_model
async def drop_table(model):
    tablename = model.tablename()
    async with model.connection() as conn:
        async with conn.transaction():
            await conn.execute(f'DROP TABLE IF EXISTS {tablename}')


@ensure_model
async def create_table(model):
    cols = ', \n'.join(
        map(lambda col: col[1].pg_column_string, model._columns())
    )
    tablename = model.tablename()
    stmt = f'''
        CREATE TABLE IF NOT EXISTS {tablename} (
            {cols}
        )
    '''

    async with model.connection() as conn:
        async with conn.transaction():
            await conn.execute(stmt)
