"""Module containing various utility functions used throughout the whole project."""
import contextlib
import os
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Union

import bcrypt
import dotenv
import mysql
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursor

from .exceptions import (
    AccountDoesNotExist,
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
        cur: MySQLCursor = con.cursor()
        yield cur
    finally:
        with contextlib.suppress(mysql.connector.InternalError):
            con.commit()
        con.close()


def _get_user_id(value: str, column: str) -> Union[int, bool]:
    """Get user id from any user detail and its column.

    :param str value: Any user value stored in the database
    :param str column: Database column of the given user value

    :returns: user id on success, False upon failure

    :raises AccountDoesNotExist: if no result was found

    """
    with database_manager() as db:
        # f-string SQl injection not an issue
        sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
        result = db.execute(sql)
    try:
        return result.fetchone()[0]
    except TypeError as e:
        raise AccountDoesNotExist(e) from e


def get_user_item(
    user_identifier: Union[int, str],
    identifier_column: str,
    result_column: str,
) -> Union[int, str, datetime]:
    """Get any user value from any other user value detail and its column.

    :param str user_identifier: Any user value stored in the database
    :param str identifier_column: Database column of the given user value
    :param str result_column: Column of the wanted value

    :returns: user id on success, False upon failure

    :raises AccountDoesNotExist: if no result was found

    """
    user_id = _get_user_id(
        user_identifier,
        identifier_column,
    )  # Exception: AccountDoesNotExist
    if result_column == "id":
        return user_id
    if user_id:
        with database_manager() as db:
            # f-string SQl injection not an issue
            sql = f"SELECT {result_column} FROM lightning_pass.credentials WHERE id = {user_id}"
            result = db.execute(sql)
    return result.fetchone()[0]


def set_user_item(
    user_identifier: Union[int, str, datetime],
    identifier_column: str,
    result: Union[int, str, datetime],
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
        sql = f"UPDATE lightning_pass.credentials WHERE id = {user_identifier} SET {result_column} = {result}"
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

    def __call__(self, username: str = None) -> None:
        """Perform both pattern and existence checks.

        :param str username: Username to check, defaults to None

        """
        if not username:
            username = self._username
        self.check_username_pattern(username)
        self.check_username_existence(username)

    @staticmethod
    def check_username_pattern(username: str) -> None:
        """Check whether a given username matches a required pattern.

        Username pattern:
            1) must be at least 5 characters long
            2) mustn't contain special characters

        :param str username: Username to check

        :raises InvalidUsername: if the username doesn't match the required pattern.

        """
        if (
            # length
            len(username) < 5
            # special char
            or len(username) - len(re.findall(r"[A-Za-z0-9]", username)) > 0
        ):
            raise InvalidUsername

    @staticmethod
    def check_username_existence(username: str, exists: bool = True) -> None:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check
        :param bool exists:
            Search type, defaults to True
            1) True means that we're checking if username exists.
            2) False means that we're checking if username doesn't exist.

        :raises UsernameAlreadyExists: if positive search was True and the username already exists in the database.
        :raises AccountDoesNotExist: if positive search was False and the username was not found.

        """
        if not username:
            raise AccountDoesNotExist
        with database_manager() as db:
            # f-string SQl injection not an issue
            sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
            result = db.execute(sql)
        if not contextlib.suppress(result.fetchone()):
            if exists and len(result) <= 0:
                raise AccountDoesNotExist
            if not exists and len(result) > 0:
                raise UsernameAlreadyExists


class Password:
    """This class holds various utils connected to any password(s).

    Calling the class performs both pattern and matching case checks.

    """

    def __init__(
        self,
        password: Union[str, bytes],
        confirm_password: Union[str, bytes],
    ) -> None:
        """Construct the class.

        :param Union[str, bytes] password: First password
        :param Union[str, bytes] confirm_password: Second password

        """
        self._password = str(password)
        self.confirm_password = str(confirm_password)

    def __call__(
        self,
        password: Union[str, bytes] = None,
        confirm_password: Union[str, bytes] = None,
    ) -> None:
        """Perform both pattern and match checks.

        :param Union[str, bytes] password: First password, defaults to None
        :param Union[str, bytes] confirm_password: Second password, defaults to None

        """
        if not password:
            password = self._password
        if not confirm_password:
            confirm_password = self.confirm_password
        self.check_password_pattern(password)
        self.check_password_match(password, confirm_password)

    @staticmethod
    def check_password_pattern(password: Union[str, bytes]) -> None:
        """Check whether password matches a required pattern.

        Password pattern:
            1) must be at least 8 characters long
            2) must contain at least 1 capital letter
            3) must contain at least 1 number
            4) must contain at least 1 special character

        :param Union[str, bytes] password: Password to check

        :raises InvalidPassword: if the password doesn't match the required pattern.

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
            raise InvalidPassword

    @staticmethod
    def check_password_match(
        password: Union[str, bytes],
        confirm_password: Union[str, bytes],
    ) -> None:
        """Check whether two passwords match.

        :param  Union[str, bytes] password: First password
        :param Union[str, bytes] confirm_password: Confirmation password

        :raises PasswordsDoNotMatch: if password and confirm password don't match.

        """
        # If password bytes, turn into str
        password, confirm_password = (str(x) for x in (password, confirm_password))
        if not secrets.compare_digest(password, confirm_password):
            raise PasswordsDoNotMatch

    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password by bcrypt with "utf-8" encoding and gensalt().

        :param str password: Password to hash

        :returns: hashed password by bcrypt

        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def authenticate_password(
        password: Union[str, bytes],
        current_password: Union[str, bytes],
    ) -> None:
        """Check if passwords match.

        :param Union[str, bytes] password: Entered password.
        :param Union[str, bytes] current_password: Password stored in the database.
        """
        if not bcrypt.checkpw(
            password.encode("utf-8"),
            current_password.encode("utf-8"),
        ):
            raise AccountDoesNotExist


class Email:
    """This class holds various utils connected to any email.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, email: str) -> None:
        """Construct the class.

        :param str email: Email to construct the class

        """
        self._email = email

    def __call__(self, email: str = None) -> None:
        """Perform both pattern and existence checks.

        :param str email: First password, defaults to None

        """
        if not email:
            email = self._email
        self.check_email_pattern(email)
        self.check_email_existence(email)

    @staticmethod
    def check_email_pattern(email: str) -> None:
        """Check whether given email matches email pattern.

        Email pattern: defined by REGEX_EMAIL constant

        :param str email: Email to check

        :raises InvalidEmail: if the email doesn't match the RegEx email pattern.

        """
        if not re.search(REGEX_EMAIL, email):
            raise InvalidEmail

    @staticmethod
    def check_email_existence(email: str) -> None:
        """Check whether an email already exists and if it matches a correct email pattern.

        :param str email: Email to check

        :raises EmailAlreadyExists: if the email already exists in the database.

        """
        with database_manager() as db:
            # f-string SQl injection not an issue
            sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
            result = db.execute(sql)
        row = result.fetchall()

        if not len(row) <= 0:
            raise EmailAlreadyExists


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
