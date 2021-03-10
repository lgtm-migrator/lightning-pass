"""This module holds various utility functions used throughout the whole project."""
import os
import pathlib
import re
import secrets
from contextlib import contextmanager
from secrets import compare_digest
from typing import Union

from bcrypt import gensalt, hashpw
from dotenv import load_dotenv
from mysql import connector

from .exceptions import (
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


@contextmanager
def database_manager() -> "connector.connection.MySQLCursor":
    """Manage database __enter__ and __exit__ easily.

    :returns: database connection cursor

    """
    load_dotenv()
    try:
        con = connector.connect(
            host=os.getenv("LOGINSDB_HOST"),
            user=os.getenv("LOGINSDB_USER"),
            password=os.getenv("LOGINSDB_PASS"),
            database=os.getenv("LOGINSDB_DB"),
        )
        cur = con.cursor()
        yield cur
    finally:
        try:
            con.commit()
        except connector.errors.InternalError:
            pass
        con.close()


def get_user_id(value: str, column: str) -> Union[int, bool]:
    """Gets user id from any user detail and its column.

    :param str value: Any user value stored in the database
    :param str column: Database column of the given user value

    :returns: user id on success, False upon failure

    """
    with database_manager() as db:
        sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
        result = db.execute(sql)

    try:
        return result.fetchone()[0]
    except TypeError:
        return False


class Username:
    """This class holds various utils connected to any username.

    :param str username: Username

    """

    def __init__(self, username: str) -> None:
        self.name = username

    def __call__(self, username: str) -> None:
        self.check_username_pattern(username)
        self.check_username_existence(username)

    @staticmethod
    def check_username_pattern(username: str) -> None:
        """Check whether a given username matches a required pattern.

        :param str username: Username to check

        :raises InvalidUsername: if the username doesn't match the required pattern.

        """
        if len(username) < 5:
            raise InvalidUsername

    @staticmethod
    def check_username_existence(username: str) -> None:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check

        :raises UsernameAlreadyExists: if the username already exists in the database.

        """
        with database_manager() as db:
            sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
            result = db.execute(sql)
        row = result.fetchall()

        if not len(row) <= 0:
            raise UsernameAlreadyExists


class Password:
    """This class holds various utils connected to any password(s).

    :param Union[str, bytes] password: Password

    """

    def __init__(
        self, password: Union[str, bytes], confirm_password: Union[str, bytes]
    ) -> None:
        self._pass = password
        self.conf_pass = confirm_password

    def __call__(
        self, password: Union[str, bytes], confirm_password: Union[str, bytes]
    ) -> None:
        self.check_password_pattern(password)
        self.check_password_match(password, confirm_password)

    @staticmethod
    def check_password_pattern(password: Union[str, bytes]) -> None:
        """Check whether password matches a required pattern.

        Password pattern: 1) must be at least 8 characters long
                          2) must contain at least 1 capital letter
                          3) must contain at least 1 number
                          4) must contain at least 1 special character

        :param Union[str, bytes] password: Password to check

        :raises InvalidPassword: if the password doesn't match the required pattern.

        """
        password = str(password)  # if password in bytes, turn into str
        if (
            len(password) < 8
            or len(re.findall(r"[A-Z]", password)) <= 0
            or len(re.findall(r"[0-9]", password)) <= 0
            or len(password) - len(re.findall(r"[A-Za-z0-9]", password)) <= 0
        ):
            raise InvalidPassword

    @staticmethod
    def check_password_match(
        password: Union[str, bytes], confirm_password: Union[str, bytes]
    ) -> None:
        """Check whether two passwords match.

        :param str password: First password
        :param Union[str, bytes] confirm_password: Confirmation password

        :raises PasswordsDoNotMatch: if password and confirm password don't match.

        """
        if not compare_digest(password, confirm_password.encode("utf-8")):
            raise PasswordsDoNotMatch

    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password by bcrypt with "utf-8" encoding and gensalt().

        :param str password: Password to hash

        :returns: hashed password by bcrypt

        """
        return hashpw(password.encode("utf-8"), gensalt())


class Email:
    """This class holds various utils connected to any username.

    :param str email: Email

    """

    def __init__(self, email: str) -> None:
        self._email = email

    def __call__(self, email: str) -> None:
        self.check_email_pattern(email)
        self.check_email_existence(email)

    @staticmethod
    def check_email_pattern(email: str) -> None:
        """Check whether given email matches email pattern.

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
            sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
            result = db.execute(sql)
        row = result.fetchall()

        if not len(row) <= 0:
            raise EmailAlreadyExists


class ProfilePicture:
    """This class holds various utils connected to any username."""

    @staticmethod
    def save_picture(picture_path: "pathlib.Path") -> str:
        """Save picture into profile pictures folder with a token_hex filename.

        Uses the monkey patched copy function of pathlib.Path object to copy the profile picture.

        :param pathlib.Path picture_path: Path to selected profile picture

        :returns: the filename of the saved picture

        """
        random_hex = secrets.token_hex(8)
        f_ext = picture_path.suffix
        picture_filename = random_hex + f_ext

        absolute_path = pathlib.Path().absolute()
        save_path = f"lightning_pass/users/profile_pictures/{picture_filename}"
        final_path = pathlib.Path.joinpath(absolute_path, save_path)

        pathlib.Path.copy(picture_path, final_path)
        return picture_filename

    @staticmethod
    def get_profile_picture_path(profile_picture: str) -> "pathlib.Path":
        """Return the absolute path of a given profile picture from the profile pictures folder.

        :param str profile_picture: Filename of the registered users' profile picture

        :returns: path to the profile picture

        """
        absolute_path = pathlib.Path().absolute()
        picture_path = f"lightning_pass/users/profile_pictures/{profile_picture}"
        return pathlib.Path.joinpath(absolute_path, picture_path)
