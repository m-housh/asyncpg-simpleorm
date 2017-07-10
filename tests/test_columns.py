import pytest
import inspect
import uuid

from .conftest import DBURI

from asyncpg_simpleorm import column, table_utils, AsyncModel, ConnectionManager
from asyncpg_simpleorm import table_utils


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
    if column_type == column.Array:
        assert not hasattr(column_type(column.String()), '__dict__')
    elif column_type in [column.Bit, column.FixedLengthString]:
        assert not hasattr(column_type(3), '__dict__')
    else:
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

    if column_type == column.Array:
        ctype = column_type(column.String())
    elif column_type in [column.Bit, column.FixedLengthString]:
        ctype = column_type(3)
    else:
        ctype = column_type()

    type_string = ctype.pg_type_string
    assert type_string

    col = column.Column('col', ctype, primary_key=True)
    expected = f'col {type_string} PRIMARY KEY'
    assert col.pg_column_string == expected


def test_Column__repr__(User):
    expected = (
        "Column(key='_id', default={}, primary_key=True, _type=uuid)"
        .format(uuid.uuid4)
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

    col = column.Column('col', _type=object)
    with pytest.raises(TypeError):
        col.pg_column_string


def test_column_factory():

    cols = (
        column.Column('id', column.String, default='paul',
                      primary_key=True),
        column.Column(column.String(), 'id', default='paul',
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


def test_Array():
    a = column.Array(column.Integer, 3)
    assert a.pg_type_string == 'integer ARRAY[3]'

    a = column.Array(column.Integer(), 3, 3)
    assert a.pg_type_string == 'integer [3][3][3]'

    a = column.Array(column.Integer, dimensions=2)
    assert a.pg_type_string == 'integer [][]'


def test_Array_fails():
    with pytest.raises(TypeError):
        column.Array(object())

    with pytest.raises(TypeError):
        column.Array(object)


@pytest.mark.asyncio
async def test_ColumnTypes_create_tables(column_type):

    ctypes = []

    if column_type == column.Array:
        ctypes = [
            column_type(column.Integer),
            column_type(column.Integer(), 3),
            column_type(column.Integer(), 3, 3)
        ]
    elif column_type == column.Bit:
        ctypes = [
            column_type(3),
            column_type(3, fixed_length=True)
        ]
    elif column_type == column.FixedLengthString:
        ctypes = [column_type(3)]
    elif column_type == column.IPAddress:
        ctypes = [
            column_type(),
            column_type(inet=True)
        ]
    else:
        ctypes = [column_type()]

    for ctype in ctypes:
        class ColumnTypeTable(AsyncModel, connection=ConnectionManager(DBURI)):
            col = column.Column(ctype)

        # test that types create tables properly
        await table_utils.create_table(ColumnTypeTable)
        # drop the table after creating it.
        await table_utils.drop_table(ColumnTypeTable)
