========
Examples
========


Asyncpg-Simpleorm aids in the creation of query statements for use with
``asyncpg`` async postgres connector.  This package allows you to create model
classes (similar to sqlalchemy syntax) and can execute common database
operations.


The following example can be ran with docker-compose.

.. code-block:: bash

    $ git clone https://github.com/m-housh/asyncpg-simpleorm.git
    $ docker-compose build orm
    $ docker-compose run --rm orm python examples/user.py




db.py
~~~~~

The following is just some boiler plate to make a connection manager
that is required by our database model(s) we will create.

.. literalinclude:: ../examples/db.py

user.py
~~~~~~~

The primary class exposed by **Asyncpg-Simpleorm** is the ``AsyncModel`` class. 

The ``AsyncModel`` model class uses ``__init_subclass__`` (new in python 3.6),
to allow key word parameters in the class declaration of all subclasses.  We
use this to set a manager on the class, that is used to manage the connection
to the database, that a subclass uses in it's database interactions.

Here we use a ``PoolManager`` instance  defined in ``db.py``, we very
well could/should use the ``ConnectionManager`` class that just manages a single
connection, however if you are using the same manager for multiple database 
models, then the ``PoolManager`` makes more sense.

.. literalinclude:: ../examples/user.py


run.py
~~~~~~

.. literalinclude:: ../examples/run.py

Running this example should output something like the following.

output
~~~~~~

.. code-block:: python

    Let's create some users...
    Saving user: User(name='foo', email='foo@example.com', id=0cc2385f-d855-4d55-a7cc-398b176e120f)
    Saving user: User(name='bar', email='bar@example.com', id=cebf4997-f857-49f1-9391-4835003eb980)
    Saving user: User(name='baz', email='baz@example.com', id=c722d54e-5b68-4ea5-85c9-d8e31ba95bfa)
    
    
    Getting users as asyncpg.Records...
    <Record name='foo' email='foo@example.com' _id=UUID('0cc2385f-d855-4d55-a7cc-398b176e120f')>
    <Record name='bar' email='bar@example.com' _id=UUID('cebf4997-f857-49f1-9391-4835003eb980')>
    <Record name='baz' email='baz@example.com' _id=UUID('c722d54e-5b68-4ea5-85c9-d8e31ba95bfa')>
    
    
    Getting users as User instances...
    User(name='foo', email='foo@example.com', id=0cc2385f-d855-4d55-a7cc-398b176e120f)
    User(name='bar', email='bar@example.com', id=cebf4997-f857-49f1-9391-4835003eb980)
    User(name='baz', email='baz@example.com',
    id=c722d54e-5b68-4ea5-85c9-d8e31ba95bfa)
    
    
    Getting 'foo' user
    <Record name='foo' email='foo@example.com' _id=UUID('0cc2385f-d855-4d55-a7cc-398b176e120f')>
    
    
    Deleting users...
    Deleting user: User(name='foo', email='foo@example.com', id=0cc2385f-d855-4d55-a7cc-398b176e120f)
    Deleting user: User(name='bar', email='bar@example.com', id=cebf4997-f857-49f1-9391-4835003eb980)
    Deleting user: User(name='baz', email='baz@example.com', id=c722d54e-5b68-4ea5-85c9-d8e31ba95bfa)
    
    
    Dropping users table...
