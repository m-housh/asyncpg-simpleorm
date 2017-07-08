from asyncpg_simpleorm import ModelABC, BaseModel, Column
from asyncpg_simpleorm.async_model import _quote_if_str
import uuid


def test__quote_if_str():
    assert _quote_if_str('string') == "'string'"
    not_str = object()
    assert _quote_if_str(not_str) == not_str


def test_is_ModelABC():

    assert issubclass(BaseModel, ModelABC)
    assert isinstance(BaseModel(), ModelABC)
    assert not issubclass(object, ModelABC)
    assert not isinstance(object(), ModelABC)


def test_Column_descriptior(User):

    assert isinstance(User.id, Column)
    assert isinstance(User().id, uuid.UUID)

    user1 = User(name='user1')
    user2 = User()

    assert user1.id != user2.id
    assert user1.name == 'user1'
    assert user2.name == 'test'


def test_BaseModel_column_names(User):

    assert User.column_names() == ('_id', 'name', 'email')
    assert User().column_names() == User.column_names()
    assert User.attr_name_for_column('_id') == 'id'


def test_BaseModel_tablename(User):
    assert User.tablename() == 'users'
    assert User.tablename() == User().tablename()
    assert BaseModel.tablename() == 'basemodel'


def test_BaseModel_primary_keys(User):
    assert User.primary_keys() == ('_id', )
