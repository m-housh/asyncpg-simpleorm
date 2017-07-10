=====
Usage
=====

Asyncpg-Simpleorm requires python >= 3.6.

To use asyncpg-simpleorm in a project::

    import asyncpg_simpleorm


Asyncpg-Simpleorm aids in the creation of query statements for use with
``asyncpg`` async postgres connector.  This package allows you to create model
classes (similar to sqlalchemy syntax) and can execute common database
operations.

-------------------
Connection Managers
-------------------

Before we discuss creating database model's we will first discuss the connection
manager classes.  These are required to instantiate an ``AsyncModel`` subclass.
These classes are used to manage the database connection that a model uses for
it's operations.

There are two builtin manager classes, ``ConnectionManager`` and
``PoolManager``.  These mimic the contructors for ``asyncpg.connect`` and
``asyncpg.create_pool``.  Internally these provide a common interface for the
database model's to retrieve a connection in the same way, no matter which
manager best fit's your application.  They are asynchronous context managers,
that return an ``asyncpg.Connection`` when used in an ``async with`` statement.

Most likely you will not use the manager directly, besides instantiating it and
using it in the declaration of your database models.

ConnectionManager
-----------------

This add's one additional ``kwarg``, that is not passed into the
``asyncpg.connect`` method.

keep_alive:  
~~~~~~~~~~~

If set to ``True``, then the connection is kept alive and re-used for further 
database operations.  If ``False`` (default) then the connection is closed after 
a single use and re-created upon further database operations.


.. code-block:: python

    >>> manager = ConnectionManager(
            'postgresql://user:pass@localhost:5432/database'
            keep_alive=True
        )

    >>> async with manager as connection:
            # do something with the connection


PoolManager
-----------

This does not add anything to the ``asyncpg.create_pool`` method, when this
class is used as a manager, then when used as an async context manager, it
will establish a connection using the ``asyncpg.Pool.acquire()`` method, and
will then ``release`` the connection after it's use.

This is probably the best option if create multiple database model's that
share the same manager.  For example declaring a custom base model, that all
your database model's inherit from.


.. code-block:: python

    >>> manager = PoolManager(
            'postgresql://user:pass@localhost:5432/database'
        )

    >>> async with manager as connection:
            # do something with the connection

-------------------------
Creating Database Model's
-------------------------

Database models are created by subclassing ``AsyncModel`` and providing a
``Connection Manager`` instance in the class declaration.


AsyncModel
----------

The ``AsyncModel`` is the main class that a user needs to subclass to create a
representation of a database table.  That subclass can then be used for common
database operations on that table.


``AsyncModel`` uses the ``__init_subclass__`` feature new in python 3.6, which
is why the ``Connection Manager`` is passed directly into the class declaration 
using the ``connection`` kwarg.

**An example User model:**

.. code-block:: python

    >>> import asyncpg_simpleorm as orm

    >>> DB_URI = 'postgresql://user:pass@localhost:5432/database'
    
    >>> class User(orm.AsyncModel, connection=orm.ConnectionManager(DB_URI)):
    ...     __tablename__ = 'users'
    ...     _return_records = False
    ...     id = orm.Column('_id', orm.UUID(), default=uuid.uuid4, primary_key=True)
    ...     name = orm.Column(orm.String(40))
    ...     email = orm.Column(orm.String(100))


Above would be equivalent to a postgres table created with::
    
    CREATE TABLE IF NOT EXISTS users (
        _id uuid PRIMARY KEY,
        name varchar(40),
        email varchar(100)
    );


__tablename__:  
~~~~~~~~~~~~~~~~

An optional property to set the table name for the model.
If this is not set, then we will default to the lowercase version of the class
name.  This property is used in every database operation for this model.  It is
likely that in future releases, that this will be added as an option in the
``__init_subclass__`` class constructor.  However it is there and has the naming
convention to be similar to ``sqlalchemy``'s database model's.

_return_records:  
~~~~~~~~~~~~~~~~

An optional boolean set on a subclass to change the
behavior of any ``get`` operations.  The default is ``True`` which returns
instances of ``asyncpg.Record`` instances from ``get`` queries.

Returning records can also be overridden for each call to a ``get`` method, so
this is really dependant upon your use case.
    
The decision to return ``asyncpg.Record`` instances is purely based on the fact
that the design of this package is primarily to aid in the creation of database
statements and queries, and the ``asyncpg.Record`` , being more of a ``dict`` 
like object, fits better into returning ``json`` responses from an API layer.
    
It should be noted that we do not implement the ``__getitem__`` and
``__setitem__`` methods, so instances of an ``AsyncModel`` subclass use ``.``
style attribute access where ``asyncpg.Records`` use the ``[key]`` dict syntax.

instantiation
~~~~~~~~~~~~~

Subclasses of ``AsyncModel`` are instantiated with ``kwargs`` with key's mapping
to the column name.  If a ``Column`` is declared with a ``default`` parameter
then that will be used if no value is passed in for that column.

.. code-block:: python

    >>> User(name='bob')
    User(id=3d9f117a-ae5d-47a9-9617-bbc97048db14, name='bob', email=None)

Under the hood we don't do any validation or type checking on the parameters.
Failures will bubble up when trying to save to the database.  

.. code-block:: python

    >>> User(id=123)
    User(id=123, name=None, email=None)


However column values can be set with the database column name (if differs from
the attribute name)

.. code-block:: python

    >>> User(_id=123)
    User(id=123, name=None, email=None)
    >>> user = User()
    >>> setattr(user, '_id', 123)
    >>> repr(user)
    User(id=123, name=None, email=None)

The above functionality is not dependant on the default ``__init__`` method, so
an ``AsyncModel`` subclass is welcome to declare a custom constructor or
use the default.

The default constructor will actually set any ``kwarg`` as an attribute.

.. code-block:: python

    >>> User(id=123, custom_value=3)
    User(id=123, name=None, email=None, custom_value=3)

AsyncModel Database Operations
------------------------------

Subclasses built from ``AsyncModel`` have the following database operations
builtin.

save:
~~~~~

Instance method that will either update it, or create a new row in the database.  

.. code-block:: python

    >>> user = User(name='foo', email='foo@example.com')
    >>> await user.save()
    >>> user.name = 'bar'
    >>> await user.save()

get:
~~~~

A class method that retrieves model's from the database.  This method always 
returns a list of either ``asyncpg.Record`` instances, or instances of the 
database model.

.. code-block:: python

    >>> await User.get()
    [User(id=6b713a5f-c5ef-4e8e-be1c-46995f9305f4, name='bar', 
    email='foo@example.com'), ...]

Above because we declared ``_return_records`` as ``True`` we by default return
instances of the ``User`` class.  This is not the default behavior otherwise.

If you would like to get record instances.

.. code-block:: python

    >>> await User.get(records=True)
    [<Record _id=UUID('6b713a5f-c5ef-4e8e-be1c-46995f9305f4' name='bar'
    email='foo@example.com'>, ...]

If you would like to filter the query, then you can pass in ``kwargs`` where the
keys map to columns and the values are what to compare the database column to.


.. code-block:: python

    >>> await User.get(name='bar')
    [User(id=6b713a5f-c5ef-4e8e-be1c-46995f9305f4, name='bar',
    email='foo@example.com'), ]

*Currently, filter's are only compared as an exact match.*

Above would translate to.

.. code-block:: python

    stmt = '''
        SELECT (users._id, users.name, users.email) FROM users
        WHERE name = $1;
    '''
    await connection.fetch(stmt, 'bar')


get_one:
~~~~~~~~

A class method, that is the same as the ``get`` method, only it returns a single
``asyncpg.Record`` instance, or database model instance.

You would typically use this with some ``kwarg`` filter's, else it will just
return whatever database row is returned first.

.. code-block:: python

    >>> await User.get_one(name='bar')
    User(id=6b713a5f-c5ef-4e8e-be1c-46995f9305f4, name='bar',
    email='foo@example.com')

If you would like to toggle, whether to return an ``asyncpg.Record`` instance.

.. code-block:: python

    >>> await User.get_one(name='bar', record=True)
    <Record _id=UUID('6b713a5f-c5ef-4e8e-be1c-46995f9305f4' name='bar'
    email='foo@example.com'>

delete:
~~~~~~~

Instance method that will remove a database model row from the database.

.. code-block:: python

    >>> user = await User.get_one(name='bar')
    >>> await user.delete()
    >>> await user.get_one(name='bar')
    None

execute:
~~~~~~~~

A convenience class method that will execute a query inside an
``asyncpg.Connection.transaction`` block using the the database model's 
connection manager.

.. code-block:: python

    >>> stmt = 'SELECT * FROM users'
    >>> await User.execute(stmt)
    [<Record _id=UUID('6b713a5f-c5ef-4e8e-be1c-46995f9305f4' name='bar'
    email='foo@example.com'>, ...]

*See Api for full reference*

Column
------

Columns are a specialized descriptor class, that store the information
regarding the database table column.  These parameters are accessible from the
class level of the model, but not on the instance level of a model, they can have
values set or retrieved from them.  These store their value in a hidden key on
the instance, so it is currently not supported to use ``__slots__`` with an
``AsyncModel`` subclass.

key:
~~~~
    
An optional string that represents the database column name.  This is only
required when the column name is different from the attribute name you would
like the column to be accessible from at an instance of the database model.

This can be passed in as a ``kwarg`` or if ``args`` are passed in and there
is a string in the args we will use that as the key.

_type:
~~~~~~

An optional ``ColumnType``.  This is only used when using the
``create_table`` utility method.  So if you are not creating table's using
the database model, then this is not needed.

We support all postgres types.

This can be passed in as a ``kwarg`` or if ``args`` are passed in and there
is a class or instance that passes a check against ``ColumnTypeABC`` then
that will be used.

default:
~~~~~~~~

This can be a value or a callable used as the default value for an
instance.  If it is a callable, then it should take no parameters and return
a value, which is then used as the default value.

primary_key:
~~~~~~~~~~~~

Mark a column as a ``PRIMARY KEY``.  This is used in some generated queries, as
well as when creating a table from a database model.

While it shouldn't be needed, unless creating some lower level query statement's
below illustrates how accessing column parameters only works from the class
level.

.. code-block:: python

    >>> User.name.key
    name
    >>> User().name.key
    Traceback (most recent call last):
    ...
    AttributeError: 'NoneType' object has no attribute 'key'

    
Column Types
------------

# TODO:  Make column type table.
