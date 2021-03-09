"""This module holds various functions used throughout the whole project."""
import pathlib
import re
import secrets
from secrets import compare_digest

from bcrypt import gensalt, hashpw

import lightning_pass

from .exceptions import (
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


def get_user_id(value: str, column: str) -> int or bool:
    """Gets user id from any user detail and its column.

    :param str value: any user value stored in the database.
    :param str column: database column of the user value.

    :returns User id on success, False upon failure
    """
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
    cursor.execute(sql)
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return False


def check_username(username: str) -> None:
    """Check whether a username already exists in a database and if it matches a required pattern.

    :param str username: Account username

    :raises UsernameAlreadyExists: If the username already exists in the database.
    :raises InvalidUsername: If the username doesn't match the required pattern.

    """
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
    cursor.execute(sql)
    row = cursor.fetchall()

    if not len(row) <= 0:
        raise UsernameAlreadyExists
    if len(username) < 5:
        raise InvalidUsername


def check_password(password: str, confirm_password: str) -> None:
    """Check whether a password matches a required pattern and if it is the same as confirm_password.

    :param str password:
    :param str confirm_password:

    :raises InvalidPassword: If the password doesn't match the required pattern.
    :raises PasswordsDoNotMatch: If password and confirm password don't match.

    """
    if (
        len(password) < 8
        or len(re.findall(r"[A-Z]", password)) <= 0
        or len(password) - len(re.findall(r"[A-Za-z0-9]", password))
        <= 0  # Negative check for special characters
    ):
        raise InvalidPassword
    if not compare_digest(password, confirm_password):
        raise PasswordsDoNotMatch


def hash_password(password: str) -> bytes:
    """Hash password by bcrypt with "utf-8" encoding and gensalt().

    :param str password: password to an user account.

    :returns: hashed password by bcrypt.
    :rtype bytes

    """
    return hashpw(password.encode("utf-8"), gensalt())


def check_email(email: str) -> None:
    """Check whether an email already exists and if it matches a correct email pattern.

    :param str email: user's email

    :raises EmailAlreadyExists: If the email already exists in the database.
    :raises InvalidEmail: If the email doesn't match the RegEx email pattern.

    """
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
    cursor.execute(sql)
    row = cursor.fetchall()

    if not len(row) <= 0:
        raise EmailAlreadyExists
    if not re.search(REGEX_EMAIL, email):
        raise InvalidEmail


def save_picture(picture_path: pathlib.Path) -> str:
    """Save picture into profile pictures folder with a token_hex filename.

    Uses the monkey patched copy function of pathlib.Path object to copy the profile picture.

    :param pathlib.Path picture_path:

    :returns the filename of the saved picture
    :rtype str

    """
    random_hex = secrets.token_hex(8)
    f_ext = picture_path.suffix
    picture_filename = random_hex + f_ext

    absolute_path = pathlib.Path().absolute()
    save_path = f"lightning_pass/users/profile_pictures/{picture_filename}"
    final_path = pathlib.Path.joinpath(absolute_path, save_path)

    pathlib.Path.copy(picture_path, final_path)
    return picture_filename


def get_profile_picture_path(profile_picture: str) -> pathlib.Path:
    """Return the absolute path of a given profile picture from the profile pictures folder.

    :param str profile_picture: filename of the registered users profile picture

    :returns path to the profile picture.
    :rtype pathlib.Path

    """
    absolute_path = pathlib.Path().absolute()
    picture_path = f"lightning_pass/users/profile_pictures/{profile_picture}"
    return pathlib.Path.joinpath(absolute_path, picture_path)
