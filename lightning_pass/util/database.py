"""Module containing various utils connected to database management."""
import contextlib
import functools
from typing import Callable, Iterator

import mysql
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor


@contextlib.contextmanager
def database_manager() -> Iterator[None]:
    """Manage database queries easily with context manager.

    Automatically yields the database connection on __enter__ and closes the
        connection on __exit__.

    :returns: database connection cursor

    """
    from lightning_pass.settings import DB_DICT

    try:
        con: MySQLConnection = mysql.connector.connect(
            host=DB_DICT["host"],
            user=DB_DICT["user"],
            password=DB_DICT["password"],
            database=DB_DICT["database"],
        )
        # fix unread results with buffered cursor
        cur: MySQLCursor = con.cursor(buffered=True)
    except mysql.connector.errors.InterfaceError as e:
        raise ConnectionRefusedError(
            "Please make sure that your database is running."
        ) from e
    else:
        yield cur
    finally:
        with contextlib.suppress(UnboundLocalError):
            con.commit()
            con.close()


def enable_database_safe_mode(func: Callable) -> Callable:
    """Decorate func to temporarily enable safe updates in database queries.

    :param: Callable func: Function to decorate

    :returns:the decorated function

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        """Wrap the functions by 2 extra queries on __enter__ and __exit__.

        Two context managers are needed so that each query is actually committed to the database.

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


class EnableDBSafeMode:
    def __enter__(self):
        """Disable database safe mode on enter."""
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 0"
            db.execute(sql)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Enable safe mode again on exit."""
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 1"
            db.execute(sql)


__all__ = ["database_manager", "EnableDBSafeMode"]
