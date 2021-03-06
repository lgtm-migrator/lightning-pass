import pathlib
import re
import secrets
from secrets import compare_digest

from bcrypt import gensalt, hashpw

import lightning_pass
from lightning_pass.users.exceptions import Exceptions as Exc

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


def get_user_id(value, column):
    """Return user id from any user detail and its column."""
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
    cursor.execute(sql)
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return False


def check_username(username):
    """Check whether a username already exists in a database and if it matches a required pattern."""
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
    cursor.execute(sql)
    row = cursor.fetchall()

    if not len(row) <= 0:
        raise Exc.UsernameAlreadyExists
    elif len(username) < 5:
        raise Exc.InvalidUsername


def check_password(password, confirm_password):
    if (
        len(password) < 8
        or len(re.findall(r"[A-Z]", password)) <= 0
        or len(re.findall(r"[0-9~!@#$%^&*()_+/\[\]{}:'\"<>?|;-\\]", password)) <= 0
    ):
        raise Exc.InvalidPassword
    elif not compare_digest(password, confirm_password):
        raise Exc.PasswordsDoNotMatch


def hash_password(password):
    """Return a hashed password."""
    return hashpw(password.encode("utf-8"), gensalt())


def check_email(email):
    """Check whether an email already exists and if it matches a correct email pattern."""
    cursor, _ = lightning_pass.connect_to_database()
    sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
    cursor.execute(sql)
    row = cursor.fetchall()

    if not len(row) <= 0:
        raise Exc.EmailAlreadyExists
    elif not re.search(REGEX_EMAIL, email):
        raise Exc.InvalidEmail


def save_picture(picture_path):
    """Save picture into profile pictures folder with a token_hex filename. Returns the filename."""
    random_hex = secrets.token_hex(8)
    f_ext = picture_path.suffix
    picture_filename = random_hex + f_ext

    absolute_path = pathlib.Path().absolute()
    save_path = f"lightning_pass/gui/static/profile_pictures/{picture_filename}"
    final_path = pathlib.Path.joinpath(absolute_path, save_path)

    pathlib.Path.copy(picture_path, final_path)
    return picture_filename


def profile_picture_path(profile_picture):
    """Return the absolute path of a given profile picture from the profile pictures folder."""
    absolute_path = pathlib.Path().absolute()
    picture_path = f"lightning_pass/gui/static/profile_pictures/{profile_picture}"
    return pathlib.Path.joinpath(absolute_path, picture_path)
