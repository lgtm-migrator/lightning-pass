"""Module containing various functions connected to credentials used throughout the whole project."""
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import bcrypt
import yagmail
from PyQt5 import QtCore

from lightning_pass.settings import EMAIL_DICT, PFP_FOLDER

from .database import database_manager, enable_database_safe_mode
from .exceptions import (
    AccountException,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)


def _get_user_id(column: str, value: str) -> Union[int, bool]:
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
        result = db.fetchone()
    try:
        return result[0]
    except TypeError as e:
        raise AccountException from e


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
    user_identifier: Union[int, str, datetime],
    identifier_column: str,
    result: Union[int, str, bytes, datetime],
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
        sql = f"UPDATE lightning_pass.credentials SET {result_column} = '{result}' WHERE id = {user_identifier}"
        db.execute(sql)


def _check_item_existence(
    item: str,
    item_column: str,
    table: str = "credentials",
    should_exist: Optional[bool] = False,
    second_key: Optional[int] = None,
    second_key_column: Optional[str] = None,
) -> bool:
    """Check if a given item exists in the database.

    :param str item: The item by which to check the column
    :param str item_column: The column where the given time should exist
    :param str table: Specify the database where the item should exist, defaults to 'credentials'
    :param bool should_exist: Define how to approach the existence checking, defaults to False.
        1) False - Item can not exist to pass the check
        2) True - Item has to exist to pass the check
    :param int second_key: Define extra condition for existence check
    :param str second_key_column: Second key column

    :returns: boolean value indicating whether the item exists or not.

    """
    if second_key is not None and second_key_column is not None:
        sql = f"""SELECT EXISTS(SELECT 1 FROM lightning_pass.{table}
                   WHERE {item_column} = '{item}')
                     AND {second_key_column} = {second_key}"""
    else:
        sql = f"SELECT EXISTS(SELECT 1 FROM lightning_pass.{table} WHERE {item_column} = '{item}')"

    with database_manager() as db:
        db.execute(sql)
        result = db.fetchone()[0]

    if (not result and should_exist) or (result and not should_exist):
        return False
    return True


class Username:
    """This class holds various utils connected to any username.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, username: str) -> None:
        """Construct the class.

        :param str username: Username

        """
        self._username = username

    def __call__(
        self, should_exist: bool, username: Optional[str] = None
    ) -> Optional[bool]:
        """Perform both pattern and existence checks (+ raise exceptions for flow control).

        :param bool should_exist: Defines how to approach username existence check
        :param str username: Username to check, defaults to None and uses class attribute

        :returns: True if all checks have passed

        :raises AccountException: if there is no username to check
        :raises InvalidUsername: if pattern check fails
        :raises UsernameAlreadyExists: if existence check fails

        """
        if not username and self._username:
            username = self._username
        if not self.check_username_pattern(username):
            raise InvalidUsername
        if not self.check_username_existence(username, should_exist=should_exist):
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
    def check_username_existence(
        username: str, should_exist: Optional[bool] = False
    ) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check
        :param bool should_exist: Influences the checking approach, defaults to False

        :returns: True or False depending on the result

        """
        return _check_item_existence(username, "username", should_exist=should_exist)


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
        password: Optional[Union[str, bytes]] = None,
        confirm_password: Optional[Union[str, bytes]] = None,
    ) -> Optional[bool]:
        """Perform both pattern and match checks (+ raise exceptions for flow control).

        :param Union[str, bytes] password: First password, defaults to None
        :param Union[str, bytes] confirm_password: Second password, defaults to None

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
    def check_password_pattern(password: Union[str, bytes]) -> bool:
        """Check whether password matches a required pattern.

        Password pattern:
            1) must be at least 8 characters long
            2) must contain at least 1 capital letter
            3) must contain at least 1 number
            4) must contain at least 1 special character

        :param Union[str, bytes] password: Password to check

        :returns: True or False depending on the pattern check

        """
        # if password in bytes, cast into str
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
        password: Union[str, bytes],
        confirm_password: Union[str, bytes],
    ) -> bool:
        """Check whether two passwords match.

        :param  Union[str, bytes] password: First password
        :param Union[str, bytes] confirm_password: Confirmation password

        :returns: True or False depending on the result of the comparison

        """
        # if password in bytes, turn into str
        password, confirm_password = (str(x) for x in (password, confirm_password))
        return secrets.compare_digest(password, confirm_password)

    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password by bcrypt with "utf-8" encoding and a salt.

        :param str password: Password to hash

        :returns: hashed password by bcrypt

        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def authenticate_password(
        password: Union[str, bytes],
        current_password: Union[str, bytes],
    ) -> bool:
        """Check if passwords match.

        :param Union[str, bytes] password: Entered password.
        :param Union[str, bytes] current_password: Password stored in the database.

        :returns: True or False based on the authentication result

        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            current_password.encode("utf-8"),
        )


class Email:
    """This class holds various utils connected to any email.

    Calling the class performs both pattern and existential checks.

    """

    def __init__(self, email: Optional[str]) -> None:
        """Construct the class.

        :param str email: Email to construct the class

        """
        self._email = email

    def __call__(self, email: Optional[str] = None) -> bool:
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

        :param str email: Email to check

        :returns: boolean value depending on the pattern check

        """
        regex_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,4}$"
        try:
            return bool(re.search(regex_email, email))
        except TypeError:
            return False

    @staticmethod
    def check_email_existence(email: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether an email already exists.

        :param str email: Email to check
        :param should_exist: Specify the logic of the existence check

        :returns: True or False depending on the existence check

        """
        return _check_item_existence(email, "email", should_exist=should_exist)

    @classmethod
    def send_reset_email(cls, email: str) -> None:
        """Send a email with instructions on how to reset a password.

        Email contains the reset token and some general information.

        :param str email: Recipients email

        """
        if cls.check_email_existence(email, should_exist=True):
            yag = yagmail.SMTP(
                {EMAIL_DICT["username"]: "lightning_pass@noreply.com"},
                EMAIL_DICT["password"],
            )
            yag.send(
                to=email,
                subject="Lightning Pass - reset password",
                contents=f"""You have requested to reset your password in Lightning Pass.
Please enter the reset token below into the application.
    
{Token.generate_reset_token(get_user_item(email, "email", "id"))}

If you did not make this request, ignore this email and no changes will be made to your account.""",
            )
        else:
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(2000, loop.quit)
            loop.exec_()


class ProfilePicture:
    """This class holds various utils connected to any profile picture."""

    @staticmethod
    def save_picture(picture_path: Path) -> str:
        """Save picture into profile pictures folder with a token_hex filename.

        Uses the monkey patched copy function of Path object to copy the profile picture.

        :param Path picture_path: Path to selected profile picture

        :returns: the filename of the saved picture

        """
        picture_filename = secrets.token_hex(8) + picture_path.suffix
        final_path = PFP_FOLDER / picture_filename
        Path.copy(picture_path, final_path)
        return picture_filename

    @staticmethod
    def get_profile_picture_path(profile_picture: str) -> Path:
        """Return the absolute path of a given profile picture from the profile pictures folder.

        :param str profile_picture: Filename of the registered users' profile picture

        :returns: path to the profile picture

        """
        return PFP_FOLDER / profile_picture


class Token:
    """This class holds various utils connected to token generation and checking."""

    @staticmethod
    @enable_database_safe_mode
    def generate_reset_token(user_id: int) -> str:
        """Clear all tokens older than 30 minutes. Insert new user's token into database and return it.

        Database safe mode is used for the first query where the search is not based on the primary key.

        :param int user_id: Used to create a reference between the user and his token.

        :returns: generated token

        """
        token = secrets.token_hex(15) + str(user_id)
        with database_manager() as db:
            sql = "DELETE FROM lightning_pass.tokens WHERE creation_date < (NOW() - INTERVAL 30 MINUTE)"
            db.execute(sql)

            sql = f"INSERT INTO lightning_pass.tokens (user_id, token) VALUES ({user_id}, '{token}')"
            db.execute(sql)
        return token

    @staticmethod
    def check_token_existence(token: str) -> Optional[bool]:
        """Check if it's possible to use the entered token.

        If token is valid, delete it from the database and proceed

        :param str token: The token to evaluate

        :returns: True if everything went correctly, False if token is invalid

        """
        if _check_item_existence(token, "token", "tokens", should_exist=True):
            with database_manager() as db:
                sql = f"DELETE FROM lightning_pass.tokens WHERE token = '{token}'"
                db.execute(sql)
            return True
        return False


__all__ = [
    "Email",
    "Password",
    "ProfilePicture",
    "Username",
    "database_manager",
    "get_user_item",
    "set_user_item",
]
