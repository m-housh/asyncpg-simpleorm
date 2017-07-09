import pytest
import inspect

from asyncpg_simpleorm import column
import uuid


def _col_types():
    """Iterates through the ``asyncpg_simpleorm.column`` module yielding the
    ``ColumnType`` subclasses.

    """
    for value in vars(column).values():
        if inspect.isclass(value):
            if issubclass(value, column.ColumnTypeABC) and \
                    value not in (column.ColumnTypeABC, column.ColumnType):
                yield value


@pytest.fixture(params=list(_col_types()))
def column_type(request):
    return request.param


def test_ColumnTypes__slots__(column_type):
    assert not hasattr(column_type(), '__dict__')


def test_ColumnType_subclass_fails():

    with pytest.raises(RuntimeError):
        class Fail(column.ColumnType):
            pass


    with pytest.raises(RuntimeError):
        class Fail2(column.ColumnType, pg_type_string='string'):
            # init with no declared __slots__ fails
            def __init__(self):
                pass


def test_ColumnType_pg_column_string(column_type):

    assert issubclass(column_type, column.ColumnTypeABC)

    type_string = column_type().pg_type_string
    assert type_string

    col = column.Column('col', column_type(), primary_key=True)
    print('col', col)
    expected = f'col {type_string} PRIMARY KEY'
    assert col.pg_column_string == expected


def test_Column__repr__(User):
    expected = (
        "Column(key='_id', default={}, primary_key=True, _type=uuid)".format(
        uuid.uuid4)
    )
    assert repr(User.id) == expected


def test_User_column_types(User):

    assert User.id.pg_column_string == '_id uuid PRIMARY KEY'
    assert User.name.pg_column_string == 'name varchar(40)'
    assert User.email.pg_column_string == 'email text'


def test_ColumnType_pg_column_string_fails():

    col = column.Column('col')
    with pytest.raises(TypeError):
        col.pg_column_string

    col = column.Column('col', type=object)
    with pytest.raises(TypeError):
        col.pg_column_string


def test_column_factory():

    cols = (
        column.create_column('id', column.String, default='paul',
                             primary_key=True),
        column.create_column(column.String(), 'id', default='paul',
                             primary_key=True),
    )
    for col in cols:
        if inspect.isclass(col._type):
            assert col._type == column.String
        else:
            assert isinstance(col._type, column.String)
        assert col.key == 'id'
        assert col.primary_key is True
        assert col.default == 'paul'
