.. _api:

==============
API Referenece
==============

.. module:: asyncpg_simpleorm

.. autoclass:: AsyncModel
    :members:
    :noindex:

Connection Manager's
--------------------

.. autoclass:: ConnectionManager
    :members:
    :noindex:

.. autoclass:: PoolManager
    :members:
    :noindex:

Column
------

.. autoclass:: Column
    :members:
    :noindex:

Column Types
------------

The following :class:`ColumnType` classes are used when creating table's using
the :func:`create_table` function.

These are used in conjunction with the :class:`Column` class.  They do not do
any type checking or validation.  They only generate column type strings during
table creation.


.. autoclass:: ColumnType
    :members:
    :noindex:

Array Types
~~~~~~~~~~~

.. autoclass:: Array
    :members:
    :noindex:

Character / String Types
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: String
    :members:
    :noindex:

.. autoclass:: FixedLengthString
    :members:
    :noindex:

Boolean Type
~~~~~~~~~~~~

.. autoclass:: Boolean
    :members:
    :noindex:

Numeric Types
~~~~~~~~~~~~~

.. autoclass:: Integer
    :members:
    :noindex:

.. autoclass:: BigInteger
    :members:
    :noindex:

.. autoclass:: SmallInteger
    :members:
    :noindex:

.. autoclass:: Number
    :members:
    :noindex:

.. autoclass:: Double
    :members:
    :noindex:

.. autoclass:: Real
    :members:
    :noindex:

.. autoclass:: Money
    :members:
    :noindex:

.. autoclass:: Serial
    :members:
    :noindex:

.. autoclass:: BigSerial
    :members:
    :noindex:

.. autoclass:: SmallSerial
    :members:
    :noindex:

Date and Time Types
~~~~~~~~~~~~~~~~~~~

.. autoclass:: Date
    :members:
    :noindex:

.. autoclass:: Time
    :members:
    :noindex:

.. autoclass:: Timestamp
    :members:
    :noindex:

.. autoclass:: TimeInterval
    :members:
    :noindex:

Geometric Types
~~~~~~~~~~~~~~~

.. autoclass:: Box
    :members:
    :noindex:

.. autoclass:: Circle
    :members:
    :noindex:

.. autoclass:: Line
    :members:
    :noindex:

.. autoclass:: LineSegment
    :members:
    :noindex:

.. autoclass:: Path
    :members:
    :noindex:

.. autoclass:: Point
    :members:
    :noindex:

.. autoclass:: Polygon
    :members:
    :noindex:

JSON Types
~~~~~~~~~~

.. autoclass:: Json
    :members:
    :noindex:

.. autoclass:: JsonB
    :members:
    :noindex:

Binary Data Types
~~~~~~~~~~~~~~~~~

.. autoclass:: Binary
    :members:
    :noindex:

Network Address Types
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: IPAddress
    :members:
    :noindex:

.. autoclass:: MACAddress
    :members:
    :noindex:

Bit String Types
~~~~~~~~~~~~~~~~

.. autoclass:: Bit
    :members:
    :noindex:

Text Search Types
~~~~~~~~~~~~~~~~~

.. autoclass:: TextSearchQuery
    :members:
    :noindex:

.. autoclass:: TextSearchVector
    :members:
    :noindex:

UUID Type
~~~~~~~~~

.. autoclass:: UUID
    :members:
    :noindex:

XML Type
~~~~~~~~

.. autoclass:: XML
    :members:
    :noindex:

Range Types
~~~~~~~~~~~

.. autoclass:: IntegerRange
    :members:
    :noindex:

.. autoclass:: NumericRange
    :members:
    :noindex:

.. autoclass:: DateRange
    :members:
    :noindex:

Miscellaneous Types
~~~~~~~~~~~~~~~~~~~

.. autoclass:: PGLogSequenceNumber
    :members:
    :noindex:

.. autoclass:: TransactionID
    :members:
    :noindex:


Table Utilities
---------------

.. autofunction:: create_table
    :noindex:

.. autofunction:: drop_table
    :noindex:

.. autofunction:: truncate_table
    :noindex:

Examples
~~~~~~~~

Using the ``User`` model from the ``Usage`` section.

.. code-block:: python
    
    >>> import asyncpg_simpleorm as orm
    >>> await orm.create_table(User)

.. code-block:: python

    >>> user = User(name='foo', email='foo@example.com')
    >>> await user.save()
    >>> await orm.truncate_table()  # keep the table schema, but delete all rows
    >>> print(await User.get())
    []

.. code-block:: python

    >>> await orm.drop_table(User)
    >>> print(await User.get())
    Traceback (most recent call last):
    ...
    asyncpg.exceptions.UndefinedTableError: relation "users" does not exist


Statements
----------

Statements are a lower level concept, and most likely not needed by most
consumers of this package, unless trying to implement some custom database query
statement generators.

The main concept behind a statment is that given an :class:`AsyncModel`, they
should generate a query string (and possibly query args) to be used for database
operations.

The statement classes when iterated over should return at minimum a string and
possibly args.  This allows a statement to be executed with
``connection.execute(*statement)`` syntax.


Example
~~~~~~~

Using the ``User`` class from the ``Usage`` section. And the ``update``
statement factory.

.. code-block:: python

    >>> user = User(id=123, name='foo', email='foo@example.com')
    >>> stmt = update(user)
    >>> q = stmt.query()  # Return's a tuple of ``(string, arg1, ...argn)``
    >>> print(q[0])
    UPDATE users SET (_id, name, email) = ($1, $2, $3)
    WHERE users._id = $4
    >>> print(q[1:])  # the ``args``.
    (123, 'foo', 'foo@example.com', 123)

Execute the statement with an ``asyncpg.Connection``

.. code-block:: python

    >>> response = await connection.execute(*stmt)
    UPDATE 0 1


.. autofunction:: select
    :noindex:

.. autofunction:: insert
    :noindex:

.. autofunction:: update
    :noindex:

.. autofunction:: delete
    :noindex:

.. autoclass:: Statement
    :members:
    :noindex:


Abstract and Base Classes
-------------------------

.. autoclass:: BaseModel
    :members:
    :noindex:

.. autoclass:: BaseStatement
    :members:
    :noindex:

.. autoclass:: AsyncModelABC
    :members:
    :noindex:

.. autoclass:: AsyncContextManagerABC
    :members:
    :noindex:

.. autoclass:: ColumnTypeABC
    :members:
    :noindex:

.. autoclass:: StatementABC
    :members:
    :noindex:


Exceptions
----------

.. automodule:: asyncpg_simpleorm.exceptions
    :members:
    :noindex:

