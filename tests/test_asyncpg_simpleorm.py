import pytest
import uuid
import random
import asyncpg
from asyncpg_simpleorm import AsyncModel, ExecutionFailure, PoolManager, \
    ConnectionManager, AsyncContextManagerABC, AsyncModelABC


pytestmark = pytest.mark.asyncio


async def test_AsyncModelABC(User):
    assert issubclass(User, AsyncModelABC)
    assert isinstance(User(), AsyncModelABC)

    assert not issubclass(object, AsyncModelABC)
    assert not isinstance(object(), AsyncModelABC)


async def test_AsyncContextManagerABC(User):
    assert issubclass(ConnectionManager, AsyncContextManagerABC)
    assert issubclass(PoolManager, AsyncContextManagerABC)
    assert isinstance(User.connection(), AsyncContextManagerABC)
    assert not issubclass(object, AsyncContextManagerABC)
    assert not isinstance(object(), AsyncContextManagerABC)


async def test_Column__repr__(User):
    expected = "Column(key='_id', default={}, primary_key=True)".format(
        uuid.uuid4)
    assert repr(User.id) == expected


async def test_AsyncModel_connection(User):
    connection = User.connection()
    assert isinstance(connection, AsyncContextManagerABC)
    assert type(connection) in (ConnectionManager, PoolManager)


async def test_AsyncModel__init_subclass__():

    with pytest.raises(RuntimeError):

        class Fail(AsyncModel, connection=object()):
            pass

async def test_save(User):

    user = User(name='jim', email='jim@foo.com')
    await user.save()

    res = await User.get_one(id=user.id)
    assert res['_id'] == user.id
    assert res['name'] == user.name
    assert res['email'] == user.email


async def test_save_as_update(User):
    await User.populate(1)
    user = await User.get_one(record=False)
    user.name = 'foo-bar'
    await user.save()

    res = await User.get_one(record=False, id=user.id)
    assert res.name == 'foo-bar'


async def test_save_fails(User):

    with pytest.raises(asyncpg.exceptions.NotNullViolationError):
        user = User(name='fail')
        await user.save()
        print('user', user, '\n', await User.get_one(id=user.id))
        assert 0


async def test_get(User):
    expected = 20
    await User.populate(expected)

    res = await User.get(records=False)
    assert len(res) >= expected

    for u in res:
        assert isinstance(u, AsyncModel)

    # test with **kwargs
    user = random.choice(res)
    name = getattr(user, 'name')
    res = await User.get(name=name)
    assert len(res) == 1
    assert not isinstance(res[0], AsyncModel)
    assert res[0]['name'] == name


async def test_delete(User):
    await User.populate(20)

    res = await User.get(records=False)
    assert len(res) > 0
    for u in res:
        await u.delete()

    res = await User.get()
    assert len(res) == 0

    with pytest.raises(ExecutionFailure):
        # user has not actually been saved to the database
        # so it won't be deleted.
        u = User()
        await u.delete()
