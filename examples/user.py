"""
examples/user.py
----------------

A simple user model to show how some features of the ``asyncpg_simpleorm``
package.

"""
import uuid
from examples.db import pool_manager
import asyncpg_simpleorm as orm


class User(orm.AsyncModel, connection=pool_manager):
    """A simple user class.

    Table Columns
    -------------

    _id : uuid  Primary Key
    name : varchar(40)
    email : varchar(100)

    """
    # Set the database tablename.  If not supplied then it defaults
    # to lower case version of class name.
    __tablename__ = 'users'
    return_records = False

    id = orm.Column('_id', orm.UUID(), default=uuid.uuid4, primary_key=True)
    name = orm.Column(orm.String(40))
    email = orm.Column(orm.String(100))
