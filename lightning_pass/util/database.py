"""Module containing various utils connected to database management."""
import contextlib
from typing import TYPE_CHECKING, Iterator

import mysql.connector

if TYPE_CHECKING:
    from mysql.connector import MySQLConnection
    from mysql.connector.cursor import MySQLCursor


DATABASE_FIELDS = {
    "id",
    "username",
    "password",
    "email",
    "profile_picture",
    "last_login_date",
    "register_date",
    "last_vault_unlock_date",
    "master_salt",
}


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


@contextlib.contextmanager
def enable_db_safe_mode() -> Iterator[None]:
    """Enable database safe mode."""
    with database_manager() as db:
        sql = "SET SQL_SAFE_UPDATES = 0"
        db.execute(sql)
    try:
        yield
    finally:
        with database_manager() as db:
            sql = "SET SQL_SAFE_UPDATES = 1"
            db.execute(sql)


__all__ = [
    "enable_db_safe_mode",
    "database_manager",
]
