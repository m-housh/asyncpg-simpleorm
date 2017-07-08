#!/usr/bin/env python
import inspect
from asyncpg_simpleorm import AsyncModel, Column, ConnectionManager
from asyncpg_simpleorm.abstract import AsyncModelABC

DB_URI = 'postgres://postgres:secret@postgres:5432/postgres'


async def create_table(model):
    if not issubclass(model, AsyncModelABC):
        raise TypeError(model)

    tablename = model.tablename()
    stmt = f'''
    CREATE TABLE IF NOT EXISTS {tablename} (
        id uuid PRIMARY KEY,
        name varchar(100) NOT NULL,
        email text
    )
    '''
    async with model.connection() as conn:
        async with conn.transaction():
            await conn.execute(stmt)


async def drop_table(model, cascade=False):
    if not issubclass(model, AsyncModelABC):
        raise TypeError(model)

    tablename = model.tablename()
    stmt = f'''DROP TABLE IF EXISTS {tablename}'''

    if cascade is True:
        stmt += ' CASCADE'

    async with model.connection() as conn:
        async with conn.transaction():
             await conn.execute(stmt)


class User(AsyncModel, connection=ConnectionManager(DB_URI)):

    __tablename__ = 'users'

    id = Column(primary_key=True)
    name = Column()
    email = Column()


async def main():
    await create_table(User)
    print(await User.get())
    await drop_table(User, True)


if __name__ == '__main__':
    import asyncio

    asyncio.get_event_loop().run_until_complete(main())
