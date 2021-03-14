"""Module containing various utility functions used throughout the whole project."""
from __future__ import annotations

import contextlib
import os
import re
import secrets
from datetime import datetime
from pathlib import Path

import bcrypt
import dotenv
import mysql
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursor

from lightning_pass.util.exceptions import (
    AccountException,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


@contextlib.contextmanager
def database_manager() -> MySQLCursor:
    """Manage database queries easily with context manager.

    Automatically yields the database connection on __enter__
    and closes the connection on __exit__.

    :Yields: database connection cursor

    """
    dotenv.load_dotenv()
    try:
        con: MySQLConnection = mysql.connector.connect(
            host=os.getenv("LOGINSDB_HOST"),
            user=os.getenv("LOGINSDB_USER"),
            password=os.getenv("LOGINSDB_PASS"),
            database=os.getenv("LOGINSDB_DB"),
        )
        # fix unread results with buffered cursor
        cur: MySQLCursor = con.cursor(buffered=True)
        yield cur
    finally:
        con.commit()
        con.close()


def _get_user_id(column: str, value: str) -> int | bool:
    """Get user id from any user detail and its column.

    :param str value: Any user value stored in the database
    :param str column: Database column of the given user value

    :returns: user id on success

    :raises AccountException: if no result was found

    """
    with database_manager() as db:
        # f-string SQl injection not an issue
        sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
        db.execute(sql)
        result = db.fetchone()[0]
    if not result:
        raise AccountException
    return result


def get_user_item(
    user_identifier: int | str,
    identifier_column: str,
    result_column: str,
) -> int | str | datetime:
    """Get any user value from any other user value detail and its column.

    :param str user_identifier: Any user value stored in the database
    :param str identifier_column: Database column of the given user value
    :param str result_column: Column of the wanted value

    :returns: user id on success, False upon failure

    :raises AccountException: if no result was found

    """
    # Exception: AccountException
    user_id = _get_user_id(
        identifier_column,
        user_identifier,
    )
    if result_column == "id":
        return user_id
    with database_manager() as db:
        # f-string SQl injection not an issue
        sql = f"SELECT {result_column} FROM lightning_pass.credentials WHERE id = {user_id}"
        db.execute(sql)
        result = db.fetchone()
    try:
        return result[0]
    except TypeError as e:
        raise AccountException from e


def set_user_item(
    user_identifier: int | str | datetime,
    identifier_column: str,
    result: int | str | datetime,
    result_column: str,
) -> None:
    """Set new user item.

    :param user_identifier: Defines a value connected to the user
    :param identifier_column: Defines the location of the value
    :param result: item to insert
    :param result_column: Column should result be inserted

    """
    if identifier_column != "id":
        user_identifier = _get_user_id(identifier_column, user_identifier)
    with database_manager() as db:
        # f-string SQl injection not an issue
        sql = f"UPDATE lightning_pass.credentials SET {result_column} = '{result}' WHERE id = {user_identifier}"
        db.execute(sql)


class Username:
    """This class holds various utils connected to any username.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, username: str) -> None:
        """Construct the class.

        :param str username: Username

        """
        self._username = username

    def __call__(self, exists: bool, username: str | None = None) -> bool | None:
        """Perform both pattern and existence checks (+ raise exceptions for flow control).

        :param bool exists: Defines how to approach username existence check
        :param str username: Username to check, defaults to None and uses class attribute

        :raises AccountException: if there is no username to check
        :raises InvalidUsername: if pattern check fails
        :raises UsernameAlreadyExists: if existence check fails

        """
        if not username and self._username:
            username = self._username
        if not self.check_username_pattern(username):
            raise InvalidUsername
        elif not self.check_username_existence(username, exists=exists):
            raise UsernameAlreadyExists
        return True

    @staticmethod
    def check_username_pattern(username: str) -> bool:
        """Check whether a given username matches a required pattern.

        Username pattern:
            1) must be at least 5 characters long
            2) mustn't contain special characters

        :param str username: Username to check

        :returns: True or False depending on the result

        """
        if (
            not username
            # length
            or len(username) < 5
            # special char
            or len(username) - len(re.findall(r"[A-Za-z0-9]", username)) > 0
        ):
            return False
        return True

    @staticmethod
    def check_username_existence(username: str, exists: bool | None = False) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check
        :param bool exists: Influences the checking type, default to False

        :returns: True or False depending on the result

        """
        with database_manager() as db:
            # f-string SQl injection not an issue
            sql = f"SELECT EXISTS(SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}')"
            db.execute(sql)
            result = db.fetchone()[0]
        if not result and exists or result and not exists:
            return False
        return True


class Password:
    """This class holds various utils connected to any password(s).

    Calling the class performs both pattern and matching case checks.

    """

    def __init__(
        self,
        password: str | bytes,
        confirm_password: str | bytes,
    ) -> None:
        """Construct the class.

        :param str | bytes password: First password
        :param str | bytes confirm_password: Second password

        """
        self._password = str(password)
        self.confirm_password = str(confirm_password)

    def __call__(
        self,
        password: str | bytes | None = None,
        confirm_password: str | bytes | None = None,
    ) -> bool | None:
        """Perform both pattern and match checks (+ raise exceptions for flow control).

        :param str | bytes password: First password, defaults to None
        :param str | bytes confirm_password: Second password, defaults to None

        :returns: True or False depending on the check results

        :raises: Invalid password: if pattern check fails
        :raises: PasswordsDoNotMatch: if password do not match (obviously)

        """
        if not password and self._password:
            password = self._password
        if not confirm_password and self.confirm_password:
            confirm_password = self.confirm_password
        if not self.check_password_pattern(password):
            raise InvalidPassword
        if not self.check_password_match(password, confirm_password):
            raise PasswordsDoNotMatch
        return True

    @staticmethod
    def check_password_pattern(password: str | bytes) -> bool:
        """Check whether password matches a required pattern.

        Password pattern:
            1) must be at least 8 characters long
            2) must contain at least 1 capital letter
            3) must contain at least 1 number
            4) must contain at least 1 special character

        :param Union[str, bytes] password: Password to check

        :returns: True or False depending on the pattern check

        """
        # if password in bytes, turn into str
        password = str(password)
        if (
            # length
            len(password) < 8
            # capital letters
            or len(re.findall(r"[A-Z]", password)) <= 0
            # numbers
            or len(re.findall(r"[0-9]", password)) <= 0
            # special chars
            or len(password) - len(re.findall(r"[A-Za-z0-9]", password)) <= 0
        ):
            return False
        return True

    @staticmethod
    def check_password_match(
        password: str | bytes,
        confirm_password: str | bytes,
    ) -> bool:
        """Check whether two passwords match.

        :param  Union[str, bytes] password: First password
        :param Union[str, bytes] confirm_password: Confirmation password

        :returns: True or False depending on the result of the comparison

        """
        # If password in bytes, turn into str
        password, confirm_password = (str(x) for x in (password, confirm_password))
        if not secrets.compare_digest(password, confirm_password):
            return False
        return True

    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password by bcrypt with "utf-8" encoding and a salt.

        :param str password: Password to hash

        :returns: hashed password by bcrypt

        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def authenticate_password(
        password: str | bytes,
        current_password: str | bytes,
    ) -> bool:
        """Check if passwords match.

        :param Union[str, bytes] password: Entered password.
        :param Union[str, bytes] current_password: Password stored in the database.

        :returns: True or False based on the authentication result

        """
        if not bcrypt.checkpw(
            password.encode("utf-8"),
            current_password.encode("utf-8"),
        ):
            return False
        return True


class Email:
    """This class holds various utils connected to any email.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, email: str | None) -> None:
        """Construct the class.

        :param str email: Email to construct the class

        """
        self._email = email

    def __call__(self, email: str | None = None) -> bool:
        """Perform both pattern and existence checks (+ raise exceptions for flow control).

        :param str email: First password, defaults to None

        :returns: True if all checks pass

        :raises InvalidEmail: if email pattern check fails
        :raises EmailAlreadyExists: if chosen email already exists in the database

        """
        if not email and self._email:
            email = self._email
        if not self.check_email_pattern(email):
            raise InvalidEmail
        if not self.check_email_existence(email):
            raise EmailAlreadyExists
        return True

    @staticmethod
    def check_email_pattern(email: str) -> bool:
        """Check whether given email matches email pattern.

        Email pattern: defined by REGEX_EMAIL constant

        :param str email: Email to check

        :returns: True or False depending on the pattern check

        """
        if not re.search(REGEX_EMAIL, email):
            return False
        return True

    @staticmethod
    def check_email_existence(email: str) -> bool:
        """Check whether an email already exists.

        :param str email: Email to check

        :returns: True or False depending on the existence check

        """
        with database_manager() as db:
            # f-string SQl injection not an issue
            sql = f"SELECT EXISTS(SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}')"
            db.execute(sql)
            result = db.fetchone()[0]
        if result:
            return False
        return True


class ProfilePicture:
    """This class holds various utils connected to any profile picture."""

    @staticmethod
    def save_picture(picture_path: Path) -> str:
        """Save picture into profile pictures folder with a token_hex filename.

        Uses the monkey patched copy function of Path object to copy the profile picture.

        :param Path picture_path: Path to selected profile picture

        :returns: the filename of the saved picture

        """
        random_hex = secrets.token_hex(8)
        f_ext = picture_path.suffix
        picture_filename = random_hex + f_ext

        absolute_path = Path().absolute()
        save_path = f"lightning_pass/users/profile_pictures/{picture_filename}"
        final_path = Path.joinpath(absolute_path, save_path)

        Path.copy(picture_path, final_path)
        return picture_filename

    @staticmethod
    def get_profile_picture_path(profile_picture: str) -> Path:
        """Return the absolute path of a given profile picture from the profile pictures folder.

        :param str profile_picture: Filename of the registered users' profile picture

        :returns: path to the profile picture

        """
        absolute_path = Path().absolute()
        picture_path = f"lightning_pass/users/profile_pictures/{profile_picture}"
        return Path.joinpath(absolute_path, picture_path)
