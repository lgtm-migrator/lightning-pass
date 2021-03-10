"""This module holds various functions used throughout the whole project."""
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


def check_username(username: str) -> None:
    """Check whether a username already exists in a database and if it matches a required pattern.

    :param str username: Account username

    :raises UsernameAlreadyExists: if the username already exists in the database.
    :raises InvalidUsername: if the username doesn't match the required pattern.

    """
    with database_manager() as db:
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
        result = db.execute(sql)

    try:
        result.fetchall()
    except AttributeError:  # Means username has not yet been taken (cur is empty).
        if len(username) < 5:
            raise InvalidUsername
    else:
        raise UsernameAlreadyExists


def check_password(password: Union[str, bytes], confirm_password: str) -> None:
    """Check whether a password matches a required pattern and if it is the same as confirm_password.

    :param str password: First password
    :param Union[str, bytes] confirm_password: Confirmation password

    :raises InvalidPassword: if the password doesn't match the required pattern.
    :raises PasswordsDoNotMatch: if password and confirm password don't match.

    """
    if (
        len(password) < 8
        or len(re.findall(r"[A-Z]", str(password)))
        <= 0  # If password in bytes, turn into str.
        or len(password) - len(re.findall(r"[A-Za-z0-9]", str(password)))
        <= 0  # Negative check for special characters
    ):
        raise InvalidPassword
    if not compare_digest(password, confirm_password.encode("utf-8")):
        raise PasswordsDoNotMatch


def hash_password(password: str) -> bytes:
    """Hash password by bcrypt with "utf-8" encoding and gensalt().

    :param str password: Password to user account.

    :returns: hashed password by bcrypt.

    """
    return hashpw(password.encode("utf-8"), gensalt())


def check_email(email: str) -> None:
    """Check whether an email already exists and if it matches a correct email pattern.

    :param str email: User's email

    :raises EmailAlreadyExists: if the email already exists in the database.
    :raises InvalidEmail: if the email doesn't match the RegEx email pattern.

    """
    with database_manager() as db:
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
        result = db.execute(sql)
    row = result.fetchall()

    if not len(row) <= 0:
        raise EmailAlreadyExists
    if not re.search(REGEX_EMAIL, email):
        raise InvalidEmail


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


def get_profile_picture_path(profile_picture: str) -> "pathlib.Path":
    """Return the absolute path of a given profile picture from the profile pictures folder.

    :param str profile_picture: Filename of the registered users' profile picture

    :returns: path to the profile picture

    """
    absolute_path = pathlib.Path().absolute()
    picture_path = f"lightning_pass/users/profile_pictures/{profile_picture}"
    return pathlib.Path.joinpath(absolute_path, picture_path)
