"""Module containing various utils connected to database management."""
import contextlib
import functools
import os
from typing import Callable

import dotenv
import mysql
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor


@contextlib.contextmanager
def database_manager() -> MySQLCursor:
    """Manage database queries easily with context manager.

    Automatically yields the database connection on __enter__ and closes the
    connection on __exit__.

    Returns:
        database connection cursor
    """
    dotenv.load_dotenv()
    try:
        con: MySQLConnection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_DB"),
        )
        # fix unread results with buffered cursor
        cur: MySQLCursor = con.cursor(buffered=True)
        yield cur
    except mysql.connector.InternalError as e:
        raise ConnectionError("Please initialize your database connection") from e
    else:
        con.commit()
    finally:
        con.close()


def enable_database_safe_mode(func: Callable) -> Callable:
    """Decorate func to temporarily enable safe updates in database queries.

    Args:
        func (Callable): Function to decorate

    Returns:
        the decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        """Wrap the functions by 2 extra queries on __enter__ and __exit__.

        Two context managers are needed so that each query is actually commited to the database.

        :return: executed function or None and shows a message box indicating needed log in

        """
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 0"
            db.execute(sql)

        val = func(*args, **kwargs)

        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 1"
            db.execute(sql)

        if val is not None:
            return val

    return wrapper
