import pytest
import asyncpg
import asyncio
import os
import random
import string
import uuid
from asyncpg_simpleorm import BaseModel, Column, AsyncModel, \
    ConnectionManager, PoolManager, String, UUID

dbuser = os.environ.get('DB_USERNAME', 'postgres')
dbpass = os.environ.get('DB_PASSWORD', 'secret')
dbhost = os.environ.get('DB_HOST', 'localhost')
dbport = os.environ.get('DB_PORT', 5432)
dbname = os.environ.get('DB_NAME', 'postgres')

DBURI = f'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'


async def _drop_db(connection, tablename):
    async with connection.transaction():
        await connection.execute(f'DROP TABLE IF EXISTS {tablename}')


async def _create_table(connection, tablename):
    async with connection.transaction():
        await connection.execute(f'''
            CREATE TABLE IF NOT EXISTS {tablename} (
                _id uuid PRIMARY KEY,
                name varchar(40) NOT NULL,
                email text NOT NULL
            )
        ''')


async def _clean_db():
    """Drop and recreate the database tables.

    """
    n = 5
    while n > 0:
        try:
            connection = await asyncpg.connect(DBURI)
            await _drop_db(connection, 'users')
            await _create_table(connection, 'users')
            await connection.close()
            break
        except asyncpg.exceptions.TooManyConnectionsError:
            await asyncio.sleep(1)
            n -= 1


@pytest.fixture(autouse=True)
def clean_db():
    asyncio.get_event_loop().run_until_complete(_clean_db())


@pytest.fixture
async def connection():
    return await asyncpg.connect(DBURI)


def random_string(size=10, chars=string.ascii_letters):
    return ''.join(random.choices(chars, k=size))


class UserModelMixin:

    __tablename__ = 'users'

    id = Column('_id', UUID(), default=uuid.uuid4, primary_key=True)
    name = Column(String(40), default='test')
    email = Column(String())

    @classmethod
    async def populate(cls, n):
        for _ in range(n):
            name = random_string()
            email = f'{name}@example.com'
            model = cls(name=name, email=email)
            await model.save()


class ConnectionManagerUser(UserModelMixin, AsyncModel,
            connection=ConnectionManager(DBURI)):
    pass


class PoolManagerUser(UserModelMixin, AsyncModel,
            connection=PoolManager(DBURI)):
    pass


@pytest.fixture(params=[ConnectionManagerUser, PoolManagerUser])
def User(request):
    return request.param


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
