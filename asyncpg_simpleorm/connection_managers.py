import asyncpg
from .abstract import AsyncContextManagerABC


class ConnectionManager(AsyncContextManagerABC):
    """An async context manager that mimics the :func:`asyncpg.connect`
    function, used with subclasses of :class:`AsyncModel`.

    :param args:  Passed to :func:`asyncpg.connect` function.
    :param keep_alive:  If ``True`` then the connection is kept alive for
                        re-use.  Else it is closed after use (default).
    :param kwargs: Passed to :func:`asyncpg.connect` function.

    """
    __slots__ = ('_args', '_kwargs', '_connection', '_keep_alive')

    def __init__(self, *args, keep_alive: bool=False, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._keep_alive = keep_alive
        self._connection = None

    async def __aenter__(self):
        if self._connection is None:
            self._connection = await asyncpg.connect(*self._args,
                                                     **self._kwargs)
        return self._connection

    async def __aexit__(self, exctype, excval, traceback):
        if self._keep_alive is False:
            await self._connection.close()
            self._connection = None


class PoolManager(AsyncContextManagerABC):
    """An async context manager that mimics the :func:`asyncpg.create_pool`
    function, used with subclasses of :class:`AsyncModel`.

    :param args:  Passed to :func:`asyncpg.create_pool` function.
    :param kwargs: Passed to :func:`asyncpg.create_pool` function.

    """
    __slots__ = ('_args', '_kwargs', '_connection', '_pool')

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._connection = None
        self._pool = None

    async def __aenter__(self):
        if self._pool is None:
            self._pool = await asyncpg.create_pool(*self._args,
                                                   **self._kwargs)
        self._connection = await self._pool.acquire()
        return self._connection

    async def __aexit__(self, exctype, excval, traceback):
        await self._pool.release(self._connection)
        self._connection = None
