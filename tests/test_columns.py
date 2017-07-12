import pytest
import inspect
import uuid
import asyncpg

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


def _column_type_instances():
    for col_type in _col_types():
        if col_type == column.String():
            yield col_type()
            yield column_type(3)
        elif col_type == column.FixedLengthString:
            yield col_type(3)
        elif col_type == column.Bit:
            yield col_type(3)
            yield col_type(3, fixed_length=True)
        elif col_type == column.Time:
            yield col_type()
            yield col_type(with_timezone=True)
        elif col_type == column.Timestamp:
            yield col_type()
            yield col_type(with_timezone=True)
        elif col_type == column.Array:
            yield col_type(column.String())
            yield col_type(column.String, n=3)
            yield col_type(column.String(), n=3, dimensions=3)
            yield col_type(column.String, dimensions=3)
        elif col_type == column.IPAddress:
            yield col_type()
            yield col_type(inet=True)
        elif col_type == column.IntegerRange:
            yield col_type()
            yield col_type(big=True)
        else:
            yield col_type()


@pytest.fixture(params=list(_column_type_instances()))
def column_type(request):
    return request.param


def test_ColumnTypes__slots__(column_type):
    assert not hasattr(column_type, '__dict__')


def test_Column_pg_column_string(column_type):
    assert isinstance(column_type, column.ColumnTypeABC)

    type_string = column_type.pg_type_string
    assert type_string

    col = column.Column('col', column_type, primary_key=True)
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


def test_Column_pg_column_string_fails():

    col = column.Column('col')
    with pytest.raises(TypeError):
        col.pg_column_string

    col = column.Column('col', _type=object)
    with pytest.raises(TypeError):
        col.pg_column_string


def test_ColumnType_pg_type_string_fails():

    with pytest.raises(TypeError):
        column.ColumnType().pg_type_string


def test_ColumnType___repr__():
    expected = "ColumnType('text')"
    assert repr(column.ColumnType('text')) == expected


def test_Column():

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

    class ColumnTypeTable(AsyncModel, connection=ConnectionManager(DBURI)):
        col = column.Column(column_type)

    # there are a few types that aren't supported/ fail on all travisci,
    # so for testing purposes, we ignore errors.
    # currently just JsonB and PGLogSequenceNumber

    # test that types create tables properly
    await table_utils.create_table(ColumnTypeTable)
    # drop the table after creating it.
    await table_utils.drop_table(ColumnTypeTable)
