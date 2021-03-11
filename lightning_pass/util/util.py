"""Module containing various utility functions used throughout the whole project."""
import os
import re
import secrets
from contextlib import contextmanager
from pathlib import Path
from secrets import compare_digest
from typing import Union

from bcrypt import gensalt, hashpw
from dotenv import load_dotenv
from mysql import connector
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursor

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
def database_manager() -> MySQLCursor:
    """Manage database queries easily with context manager.

    Automatically yields the database connection on __enter__
    and closes the connection on __exit__.

    :returns: database connection cursor

    """
    load_dotenv()
    try:
        con: MySQLConnection = connector.connect(
            host=os.getenv("LOGINSDB_HOST"),
            user=os.getenv("LOGINSDB_USER"),
            password=os.getenv("LOGINSDB_PASS"),
            database=os.getenv("LOGINSDB_DB"),
        )
        cur: MySQLCursor = con.cursor()
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
        sql = (
            "SELECT id" "  FROM lightning_pass.credentials" " WHERE %s = %s" % column,
            value,
        )
        result = db.execute(sql)

    try:
        return result.fetchone()[0]
    except TypeError:
        return False


class Username:
    """This class holds various utils connected to any username.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, username: str) -> None:
        """Main constructor.

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
            or not len(username) - len(re.findall(r"[A-Za-z0-9]", username)) <= 0
        ):
            raise InvalidUsername

    @staticmethod
    def check_username_existence(username: str) -> None:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check

        :raises UsernameAlreadyExists: if the username already exists in the database.

        """
        with database_manager() as db:
            sql = (
                "SELECT 1"
                "  FROM lightning_pass.credentials"
                " WHERE username = %s" % username
            )
            result = db.execute(sql)
        row = result.fetchone()

        if not len(row) <= 0:
            raise UsernameAlreadyExists


class Password:
    """This class holds various utils connected to any password(s).

    Calling the class performs both pattern and matching case checks.

    """

    def __init__(
        self, password: Union[str, bytes], confirm_password: Union[str, bytes]
    ) -> None:
        """Main constructor.

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
        password: Union[str, bytes], confirm_password: Union[str, bytes]
    ) -> None:
        """Check whether two passwords match.

        :param  Union[str, bytes] password: First password
        :param Union[str, bytes] confirm_password: Confirmation password

        :raises PasswordsDoNotMatch: if password and confirm password don't match.

        """
        # If password bytes, turn into str
        password, confirm_password = (str(x) for x in (password, confirm_password))
        if not compare_digest(password, confirm_password):
            raise PasswordsDoNotMatch

    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password by bcrypt with "utf-8" encoding and gensalt().

        :param str password: Password to hash

        :returns: hashed password by bcrypt

        """
        return hashpw(password.encode("utf-8"), gensalt())


class Email:
    """This class holds various utils connected to any email.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, email: str) -> None:
        """Main constructor.

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
            sql = (
                "SELECT 1"
                "  FROM lightning_pass.credentials"
                " WHERE email = %s" % email
            )
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
