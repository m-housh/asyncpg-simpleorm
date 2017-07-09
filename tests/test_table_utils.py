import pytest

from asyncpg_simpleorm import drop_table, create_table, InvalidModel, \
    truncate_table

pytestmark = pytest.mark.asyncio


async def test_drop_table(User):
    await drop_table(User, cascade=True)
    with pytest.raises(Exception):
        u = User(name='foo', email='foo@example.com')
        await u.save()

    with pytest.raises(InvalidModel):
        await drop_table(object)


async def test_create_table(User):
    await drop_table(User())
    await create_table(User)
    u = User(name='foo', email='foo@example.com')
    await u.save()

    with pytest.raises(InvalidModel):
        await create_table(object)


async def test_truncate(User):

    await User.populate(10)
    await truncate_table(User, cascade=True)
    assert len(await User.get()) == 0
