#!/usr/bin/env python
"""
examples/run.py
---------------

"""
from examples.user import User
import asyncpg_simpleorm as orm


async def create_some_users():
    """Add's some user's to the database.

    """
    for name in ['foo', 'bar', 'baz']:
        u = User(name=name, email=f'{name}@example.com')
        print(f'Saving user: {u}')
        await u.save()


async def get_users_as_records():
    """Get all user's as ``asyncpg.Record`` instances (default).

    """
    users = await User.get()

    for u in users:
        print(u)


async def get_users_as_instances():
    """Get all user's and convert them all into ``User`` instances.

    This can also be set as the default behavior if we would set
    ``_return_records`` to ``True`` on our ``User`` class.

    """
    users = await User.get(records=False)

    for u in users:
        print(u)


async def get_foo_user():
    """Get user by the name of 'foo'.  The ``get`` or ``get_one`` method's
    accept **kwargs that will set a ``where`` clause on the query, to filter
    the results.

    ``get`` always returns a list of objects, where ``get_one`` always returns
    the first object.

    """
    print(await User.get_one(name='foo'))


async def delete_all_users():
    """Delete the user's from the database.

    """
    for u in await User.get(records=False):
        print(f'Deleting user: {u}')
        await u.delete()


async def main():

    await orm.create_table(User)

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
    await orm.drop_table(User)


if __name__ == '__main__':

    import asyncio

    asyncio.get_event_loop().run_until_complete(main())
