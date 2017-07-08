#!/usr/bin/env python

from examples.db import DbModel
from asyncpg_simpleorm import Column


async def delete_users_table(conn) -> None:
    await conn.execute('DROP TABLE IF EXISTS users')


async def create_users_table(conn) -> None:
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            _id uuid PRIMARY KEY NOT NULL,
            name text NOT NULL,
            email text
        )
    ''')


class User(DbModel):
    """A simple user class.

    Table Columns
    -------------

    _id : uuid  Primary Key
    name : text  Not Null
    email : text

    """
    # Set the database tablename.  If not supplied then it defaults
    # to lower case version of class name.
    __tablename__ = 'users'

    name = Column()
    email = Column()


async def create_table():
    async with User.connection() as conn:
        await delete_users_table(conn)
        await create_users_table(conn)


async def create_some_users():

    for name in ['foo', 'bar', 'baz']:
        u = User(name=name, email=f'{name}@example.com')
        print(f'Saving user: {u}')
        await u.save()


async def get_users_as_records():
    users = await User.get()

    for u in users:
        print(u)


async def get_users_as_instances():
    users = await User.get(records=False)

    for u in users:
        print(u)


async def get_foo_user():
    print(await User.get_one(name='foo'))


async def delete_all_users():
    for u in await User.get(records=False):
        print(f'Deleting user: {u}')
        await u.delete()


async def main():

    await create_table()

    print("\n\nLet's create some users...")
    await create_some_users()

    print('\n\nGetting users as asyncpg.Records...')
    await get_users_as_records()


    print('\n\nGetting users as User instances...')
    await get_users_as_instances()

    print("\n\nGetting 'foo' user")
    await get_foo_user()

    print('\n\nDeleting users...')
    await delete_all_users()

    print('\n\nDropping users table...')
    async with User.connection() as conn:
        await delete_users_table(conn)


if __name__ == '__main__':

    import asyncio

    asyncio.get_event_loop().run_until_complete(main())
