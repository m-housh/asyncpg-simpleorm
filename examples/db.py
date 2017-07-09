"""
examples/db.py
--------------

We use a ``PoolManager`` here, but a single connection manager can be
created using orm.ConnectionManager(...)

The ``PoolManager`` mimics the ``asyncpg.create_pool`` method, passing any
*args and/or **kwargs to that method, and the ``ConnectionManager`` mimics
``asyncpg.connect``.


"""
import os

import asyncpg_simpleorm as orm


DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'postgres')


pool_manager = orm.PoolManager(
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    command_timeout=60
)
