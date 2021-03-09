import os
import pathlib
from typing import Tuple

import mysql.connector as mysql
from dotenv import load_dotenv
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor


def _copy(self: pathlib.Path, target: pathlib.Path) -> None:
    """Monkey Patch copy functionality into pathlib.Path object."""
    import shutil

    assert self.is_file()
    shutil.copy(str(self), str(target))  # str() only there for Python --version < 3.6


pathlib.Path.copy = _copy  # type: ignore


def connect_to_database() -> Tuple[MySQLCursor, MySQLConnection]:
    """Initialize database connection. Create table if not exists.

    :returns cursor, connection
    :rtype tuple

    """
    load_dotenv()
    connection = mysql.connect(
        host=os.getenv("LOGINSDB_HOST"),
        user=os.getenv("LOGINSDB_USER"),
        password=os.getenv("LOGINSDB_PASS"),
        database=os.getenv("LOGINSDB_DB"),
    )
    cursor = connection.cursor()
    sql = """CREATE TABLE if not exists credentials(
            `id` int NOT NULL AUTO_INCREMENT,
            `username` varchar(255) NOT NULL,
            `password` varchar(255) NOT NULL,
            `email` varchar(255) NOT NULL,
            `profile_picture` varchar(255) NOT NULL DEFAULT 'default.png',
            `last_login_date` timestamp NULL DEFAULT NULL,
            `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
             PRIMARY KEY(`id`)
             )
             ENGINE = InnoDB
             AUTO_INCREMENT = 1
             DEFAULT CHARSET = utf8mb4
             COLLATE = utf8mb4_0900_ai_ci
             """
    cursor.execute(sql)
    return cursor, connection
