"""Module containing various functions connected to credentials used throughout the whole project."""
import secrets
import urllib.parse as urlparse
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional, Union

import bcrypt
import validator_collection
import yagmail

import lightning_pass.util.database as database
from lightning_pass.settings import PFP_FOLDER, Credentials


def _get_user_id(column: str, value: str) -> Union[int, bool]:
    """Get user id from any user detail and its column.

    :param str value: Any user value stored in the database
    :param str column: Database column of the given user value

    :returns: user id on success

    """
    with database.database_manager() as db:
        # not using f-string due to SQL injection
        sql = """SELECT id
                   FROM lightning_pass.credentials
                  WHERE {} = {}""".format(
            column,
            "%s",
        )
        # expecting a sequence thus val has to be a tuple (created by the trailing comma)
        db.execute(sql, (value,))
        result = db.fetchone()
    try:
        return result[0]
    except TypeError:
        return False


def get_user_item(
    user_identifier: Union[int, str],
    identifier_column: str,
    result_column: str,
) -> Union[bytes, int, str, datetime]:
    """Get any user value from any other user value detail and its column.

    :param str user_identifier: Any user value stored in the database
    :param str identifier_column: Database column of the given user value
    :param str result_column: Column of the wanted value

    :returns: user item on success, False upon failure

    """
    user_id = _get_user_id(
        identifier_column,
        user_identifier,
    )
    if not user_id:
        return False
    if result_column == "id":
        return user_id
    with database.database_manager() as db:
        # not using f-string due to SQL injection
        sql = """SELECT {}
                   FROM lightning_pass.credentials
                  WHERE id = {}""".format(
            result_column,
            "%s",
        )
        # expecting a sequence thus val has to be a tuple (created by the trailing comma)
        db.execute(sql, (user_id,))
        result = db.fetchone()
    try:
        return result[0]
    except TypeError:
        return False


def set_user_item(
    user_identifier: Union[int, str, datetime],
    identifier_column: str,
    result: Union[int, str, bytes, datetime],
    result_column: str,
) -> bool:
    """Set new user item.

    :param user_identifier: Defines a value connected to the user
    :param identifier_column: Defines the location of the value
    :param result: item to insert
    :param result_column: Column should result be inserted

    """
    if identifier_column != "id":
        user_identifier = _get_user_id(identifier_column, user_identifier)
    if user_identifier:
        with database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """UPDATE lightning_pass.credentials
                        SET {} = {}
                      WHERE id = {}""".format(
                result_column,
                "%s",
                "%s",
            )
            db.execute(sql, (result, user_identifier))
        return True
    else:
        return False


def check_item_existence(
    item: str,
    item_column: str,
    table: str = "credentials",
    should_exist: Optional[bool] = False,
    second_key: Optional[int] = None,
    second_key_column: Optional[str] = None,
) -> bool:
    """Check if a given item exists in the database.

    :param item: The item by which to check the column
    :param item_column: The column where the given time should exist
    :param table: Specify the database where the item should exist, defaults to "credentials"
    :param should_exist: Define how to approach the existence checking, defaults to False.
        1) False - Item can not exist to pass the check
        2) True - Item has to exist to pass the check
    :param second_key: Define extra condition for existence check
    :param second_key_column: Second key column

    :returns: boolean value indicating whether the item exists or not.

    """
    if second_key is not None and second_key_column is not None:
        # not using f-string due to SQL injection
        sql = """SELECT EXISTS(SELECT 1
                                 FROM {}
                                WHERE {} = {}
                                  AND {} = {}
                                )""".format(
            table,
            item_column,
            "%s",
            second_key_column,
            "%s",
        )
        val = (item, second_key)
    else:
        # not using f-string due to SQL injection
        sql = """SELECT EXISTS(SELECT 1
                                 FROM {}
                                WHERE {} = {}
                                )""".format(
            table,
            item_column,
            "%s",
        )
        # expecting a sequence thus create a tuple with the trailing comma
        val = (item,)

    with database.database_manager() as db:
        db.execute(sql, val)
        result = db.fetchone()

    if (not result[0] and should_exist) or (result[0] and not should_exist):
        return False
    return True


class PasswordData(NamedTuple):
    previous_password: bytes
    confirm_previous: str
    new_password: Optional[str] = None
    confirm_new: Optional[str] = None


def hash_password(password: str) -> bytes:
    """Hash password by bcrypt with "utf-8" encoding and a salt.

    :param str password: Password to hash

    :returns: hashed password by bcrypt

    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def human_date_suffix(day: int):
    ...


def send_reset_email(email: str) -> None:
    """Send a email with instructions on how to reset a password.

    Email contains the reset token and some general information.

    :param str email: Recipients email

    """
    yag = yagmail.SMTP(
        {Credentials.email_user: "lightning_pass@noreply.com"},
        Credentials.email_password,
    )
    yag.send(
        to=email,
        subject="Lightning Pass - reset password",
        contents=f"""You have requested to reset your password in Lightning Pass.
Please enter the reset token below into the application.

{Token.generate_reset_token(get_user_item(email, "email", "id"))}

If you did not make this request, ignore this email and no changes will be made to your account.""",
    )


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


def get_profile_picture_path(profile_picture: str) -> Path:
    """Return the absolute path of a given profile picture from the profile pictures folder.

    :param str profile_picture: Filename of the registered users' profile picture

    :returns: path to the profile picture

    """
    return PFP_FOLDER / profile_picture


class Token:
    """This class holds various utils connected to token generation and checking."""

    __slots__ = ()

    @staticmethod
    def generate_reset_token(user_id: int) -> str:
        """Clear all tokens older than 30 minutes. Insert new user's token into database and return it.

        Database (un)safe mode is used for the first query where the search is not based on the primary key.

        :param int user_id: Used to create a reference between the user and his token.

        :returns: generated token

        """
        token = secrets.token_hex(15) + str(user_id)

        with database.EnableDBSafeMode(), database.database_manager() as db:
            sql = """DELETE FROM lightning_pass.tokens
                           WHERE creation_date < (NOW() - INTERVAL 30 MINUTE)"""
            db.execute(sql)

        with database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """INSERT INTO lightning_pass.tokens (user_id, token)
                          VALUES ({}, {})""".format(
                "%s",
                "%s",
            )
            db.execute(sql, (user_id, token))

        return token

    @staticmethod
    def check_token_existence(token: str) -> Optional[bool]:
        """Check if it's possible to use the entered token.

        If token is valid, delete it from the database and proceed

        :param str token: The token to evaluate

        :returns: True if everything went correctly, False if token is invalid

        """
        if check_item_existence(token, "token", "tokens", should_exist=True):
            with database.database_manager() as db:
                # not using f-string due to SQL injection
                sql = """DELETE FROM lightning_pass.tokens
                               WHERE token = {}""".format(
                    "%s",
                )
                # query expecting a sequence thus val has to be a tuple (created by the trailing comma)
                db.execute(sql, (token,))
            return True
        return False


def validate_url(url: str) -> Union[str, bool]:
    """Check whether a url is valid.

    If url was only malformed, return the fixed version.

    :param url: The url to evaluate

    """
    parsed_url = urlparse.urlparse(url)

    if not bool(parsed_url.scheme):
        parsed_url = parsed_url._replace(**{"scheme": "http"})

    if validator_collection.checkers.is_url(
        url := parsed_url.geturl().replace("///", "//"),
    ):
        return url
    return False
