"""Module containing various utils connected to database management."""
import contextlib
from typing import TYPE_CHECKING, Iterator

import mysql.connector

if TYPE_CHECKING:
    from mysql.connector import MySQLConnection
    from mysql.connector.cursor import MySQLCursor


@contextlib.contextmanager
def database_manager() -> Iterator[None]:
    """Manage database queries easily with context manager.

    Automatically yields the database connection on __enter__ and closes the
    connection on __exit__.

    :returns: database connection cursor

    """
    # avoid circular import
    from lightning_pass.settings import Credentials

    try:
        con: MySQLConnection = mysql.connector.connect(
            host=Credentials.db_host,
            user=Credentials.db_user,
            password=Credentials.db_password,
            database=Credentials.db_database,
        )
        # fix unread results with buffered cursor
        cur: MySQLCursor = con.cursor(buffered=True)
    except mysql.connector.errors.InterfaceError as e:
        raise ConnectionRefusedError(
            "Please make sure that your database is running.",
        ) from e
    else:
        yield cur
    finally:
        with contextlib.suppress(UnboundLocalError):
            con.commit()
            con.close()


class EnableDBSafeMode(contextlib.ContextDecorator):
    """Context manager and a decorator to temporarily enable database safe mode."""

    __slots__ = ()

    def __enter__(self) -> None:
        """Disable database safe mode on enter."""
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 0"
            db.execute(sql)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Enable safe mode again on exit."""
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 1"
            db.execute(sql)


__all__ = ["database_manager", "EnableDBSafeMode"]
