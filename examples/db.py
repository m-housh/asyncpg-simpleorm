import os
import uuid

import asyncpg
from asyncpg_simpleorm import AsyncModel, Column, PoolManager


DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'postgres')


# We use a ``PoolManager`` here, because all classes will
# share the same manager class.
manager = PoolManager(
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)


class DbModel(AsyncModel, connection=manager):
    """Base database model class that we inherit from.

    Adds the ``id`` column to all models that inherit from this class.  The
    ``id`` in the database will be found at a column named ``_id``.

    """
    id = Column('_id', default=uuid.uuid4, primary_key=True)
