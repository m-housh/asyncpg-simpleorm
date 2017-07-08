import pytest
from asyncpg_simpleorm.statements import Statement, select, insert, \
    update, delete, _callback, _reset_counter
from asyncpg_simpleorm.statements.base_statement import StatementValues, \
    ClauseDescriptor, StatementDescriptor
from asyncpg_simpleorm.statements.abstract import StatementABC
from asyncpg_simpleorm.exceptions import InvalidModel


def test_callback_decorator():

    class A:

        def __init__(self):
            self.valid = False

        @_callback('invalid')
        def fail(self):
            return

        @_callback('set_valid')
        def succeed(self):
            return

        def set_valid(self):
            self.valid = True
            return

    a = A()
    assert a.valid is False

    a.succeed()
    assert a.valid is True

    with pytest.raises(TypeError):
        a.fail()


def test_StatementABC():
    assert issubclass(Statement, StatementABC)
    assert isinstance(Statement(None), StatementABC)

    assert not issubclass(object, StatementABC)
    assert not isinstance(object(), StatementABC)


def test_Statement_model_property_fails():
    with pytest.raises(InvalidModel):
        Statement(object)

    with pytest.raises(InvalidModel):
        Statement(object())


def test_StatementValues():
    assert StatementValues.clauses() == ('from_', 'where')
    assert isinstance(StatementValues.from_, ClauseDescriptor)
    assert not isinstance(StatementValues.from_, StatementDescriptor)

    stmts = StatementValues.statements()
    expected = ('select', 'insert', 'update', 'delete')
    for stmt in stmts:
        assert stmt in expected

    with pytest.raises(TypeError):
        StatementValues().get_statement(strict=True)

    stmt = StatementValues()
    string = 'SELECT * FROM users WHERE id = $1'
    args = (123, )
    stmt.select = (string, args)

    assert repr(stmt) == f"StatementValues('{string}', {args})"
    assert repr(StatementValues()) == 'StatementValues(None, ())'


    # test getitem
    assert stmt['insert'] is None
    with pytest.raises(KeyError):
        stmt['invalid']

    i = iter(stmt)
    assert next(i) == 'SELECT * FROM users WHERE id = $1'
    assert next(i) == 123
    with pytest.raises(StopIteration):
        next(i)

    # not allowed to set more than 1 statement on an instance.
    # however you can set more than 1 clause
    with pytest.raises(TypeError):
        stmt.insert = 'INSERT INTO ...'


def test_Statement__column_string(User):

    assert Statement(User)._column_string(True) == \
        'users._id, users.name, users.email'


def test_Statement_fails_without_model_or_kwargs(User):

    with pytest.raises(TypeError):
        Statement().select()

    with pytest.raises(TypeError):
        Statement().insert()

    with pytest.raises(TypeError):
        Statement().from_()

    with pytest.raises(TypeError):
        Statement().update()

    with pytest.raises(TypeError):
        Statement().where()

    with pytest.raises(TypeError):
        Statement().delete()

    with pytest.raises(TypeError):
        Statement(User)._get_args_from_kwargs()

    with pytest.raises(TypeError):
        Statement(User)._parse_where_items((), (), False)


def test_select(User):
    statement = select(User)
    assert isinstance(statement, Statement)

    expected = 'SELECT users._id, users.name, users.email\nFROM users'
    assert statement.query_string() == expected
    assert str(statement) == expected


def test_insert(User):

    user = User(id=123, name='user1')
    # this is not a valid statement, but testing the ``where`` statement too.

    expected = ('INSERT INTO users (_id, name, email) VALUES ($1, $2, $3)'
                '\nWHERE users._id = $4')
    expected_args = (123, 'user1', None, 456)

    statement = insert(user).where(id=456)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args

    statement = insert(user).where(_id=456)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args


def test_insert_with_kwargs(User):

    kwargs = {
        'id': 123,
        'name': 'name',
        'email': 'mail@example.com'
    }

    expected = 'INSERT INTO users (_id, name, email) VALUES ($1, $2, $3)'
    expected_args = tuple(kwargs.values())

    statement = insert(User, id=123, name='name', email='mail@example.com')
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args

    statement = Statement(User).insert(**kwargs)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args

    kwargs2 = kwargs.copy()
    del(kwargs2['id'])
    kwargs2['_id'] = kwargs['id']

    statement = Statement(User).insert(**kwargs)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args


def test_update(User):

    user = User(id=123, name='name', email='mail@example.com')
    expected = ('UPDATE users SET (_id, name, email) = ($1, $2, $3)'
                '\nWHERE users._id = $4')
    expected_args = (123, 'name', 'mail@example.com', 123)

    statement = update(user)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args

    kwargs = {
        'id': 123,
        'name': 'name',
        'email': 'mail@example.com'
    }

    statement = Statement(User).update(**kwargs)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args

    kwargs2 = kwargs.copy()
    del(kwargs2['id'])
    kwargs2['_id'] = kwargs['id']

    statement = Statement(User).update(**kwargs2)
    assert statement.query_string() == expected
    assert statement.query_args() == expected_args


@pytest.mark.asyncio
async def test_statements_with_db(User, connection):
    user = User(name='user1', email='mail@example.com')
    statement = insert(user)
    # insert the record
    await connection.execute(*statement)
    # OR
    # await connection.execute(str(statement), *statement.query_args())
    # OR
    # await connection.execute(*statement.query())

    # check that it was inserted
    res = await connection.fetchrow(*select(User).where(name='user1'))
    assert res['_id'] == user.id
    assert res['name'] == user.name
    assert res['email'] == user.email

    # update the user
    user.name = 'newname'
    # await connection.execute(*update(user).where(id=user.id))
    await connection.execute(*update(user))

    res = await connection.fetchrow(*select(user).where(id=user.id))
    assert res['_id'] == user.id
    assert res['name'] == user.name
    assert res['name'] == 'newname'
    assert res['email'] == user.email

    # ds = delete(User).where(id=user.id)
    ds = delete(user)
    print(ds.query())
    await connection.execute(*ds)

    res = await connection.fetchrow(*select(user).where(id=user.id))
    print(res)
    assert res is None

def test_where_fails(User):

    with pytest.raises(ValueError):
        select(User).where(invalid_col='something')


def test_delete(User):

    expected = 'DELETE FROM users'
    # if you use the class as the input to delete, then you will later have
    # to call the where statement.
    stmt = delete(User)
    assert stmt.query_string() == expected

    expected = f'{expected}\nWHERE users._id = $1'
    stmt.where(id=123)
    assert stmt.query_string() == expected
    assert stmt.query_args() == (123, )

    user = User(name='test', email='test@test.com')
    # when used with an instance, the where clause is automatically
    # added for the primary keys of the model.
    stmt = delete(user)
    assert stmt.query_string() == expected
    assert stmt.query_args() == (user.id, )

    # kwargs work, if statement created with a class.
    stmt = delete(User, id=123)
    assert stmt.query_string() == expected
    assert stmt.query_args() == (123, )

    # where statement's replace and reset the counter if there is already
    # a where statement on an instance.
    stmt.where(name='test')
    assert stmt.query_string() == 'DELETE FROM users\nWHERE users.name = $1'


def test_Statement_parse_where_items(User):
    stmt = Statement(User)
    items = [('invalid', 'not in check')]
    check = ['id', 'name', 'email']

    with pytest.raises(ValueError):
        stmt._parse_where_items(items, check, strict_check=True)


def test_Statement__repr__(User):
    stmt = Statement(User)
    expected = f"Statement(statement='', model={User})"
    assert repr(stmt) == expected
