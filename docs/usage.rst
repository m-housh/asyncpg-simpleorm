=====
Usage
=====

Asyncpg-Simpleorm requires python >= 3.6.

To use asyncpg-simpleorm in a project::

    import asyncpg_simpleorm


The following example can be ran with docker-compose.

.. code-block:: bash

    $ git clone https://github.com/m-housh/asyncpg-simpleorm.git
    $ docker-compose build orm
    $ docker-compose run --rm orm python examples/user.py


Create a base class that can be used for multiple models to inherit from.

**db.py**

.. literalinclude:: ../examples/db.py


Create a simple user class.

**user.py**

.. literalinclude:: ../examples/user.py


Running this example should output something like the following.

**output**

.. code-block:: bash 

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
