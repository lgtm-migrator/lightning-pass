"""Module containing the Account class and other functions related to accounts."""
from __future__ import annotations

from datetime import datetime

import lightning_pass.util.util as utl

from ..util.exceptions import AccountDoesNotExist


class Account:
    """This class holds information about the currently logged in user."""

    def __init__(self, user_id: int = None) -> None:
        """Construct the class.

        :param int user_id: User's id, defaults to None

        """
        self.user_id = int(user_id) if user_id else None

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Account({self.user_id})"

    @classmethod
    def register(
        cls,
        username: str,
        password: bytes,
        confirm_password: str,
        email: str,
    ) -> Account:
        """Secondary constructor for register.

        :param str username: User's username
        :param bytes password: User's password
        :param str confirm_password: User's confirmed password
        :param str email: User's email

        :returns: Account object instantiated with current user id

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern
        :raises PasswordDoNotMatch: if password and confirm_password are not the same
        :raises InvalidPassword: if password doesn't match the required pattern
        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        utl.Username(username)  # Exceptions: UsernameAlreadyExists, InvalidUsername
        utl.Password(
            password,
            confirm_password,
        )  # Exceptions: PasswordDoNotMatch, InvalidPassword
        utl.Email(email)  # Exceptions: EmailAlreadyExists, Invalid email
        with utl.database_manager() as db:
            sql = (
                "INSERT INTO lightning_pass.credentials (username, password, email)"
                "     VALUES (%s, %s, %s)"
            )
            values = [username, password, email]
            db.execute(sql, values)

        return cls(utl.get_user_item(username, "username", "id"))

    @classmethod
    def login(cls, username: str, password: str) -> Account:
        """Secondary constructor for login.

        Updates last_login_date if log in is successful.

        :param str username: User's username
        :param str password: User's password

        :returns: Account object instantiated with current user id

        :raises AccountDoesNotExist: if username wasn't found in the database
        :raises AccountDoesNotExist: if password doesn't match with the hashed password in the database

        """
        utl.Username.check_username_existence(username, exists=False)

        stored_password = utl.get_user_item(username, "username", "password")

        if not utl.Password.authenticate_password(password, stored_password):
            raise AccountDoesNotExist
        account = cls(utl.get_user_item(username, "username", "id"))
        account.update_last_login_date()
        return account

    def get_value(self, result_column: str) -> str | datetime:
        """Simplify getting user values.

        :param str result_column: Column from which we're collecting the value

        :returns: the result value

        """
        return utl.get_user_item(self.user_id, "id", result_column)

    def set_value(self, result: str | datetime, result_column: str) -> None:
        """Simplify setting user values.

        :param str result: Value which we're inserting
        :param str result_column: Column where to insert the value

        """
        utl.set_user_item(self.user_id, "id", result, result_column)

    @property
    def username(self) -> str:
        """Username property.

        :returns: user's username in database

        """
        return self.get_value("username")

    @username.setter
    def username(self, value: str) -> None:
        """Set new username.

        :param str value: New username

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern

        """
        utl.Username(value)  # Exceptions: UsernameAlreadyExists, InvalidUsername
        self.set_value(value, "username")

    @property
    def password(self) -> str:
        """Password property.

        :returns: user's password in database

        """
        return self.get_value("password")

    @property
    def email(self) -> str:
        """Email property.

        :returns: user's email in database

        """
        return self.get_value("email")

    @email.setter
    def email(self, value: str) -> None:
        """Set new email.

        :param str value: New email

        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        utl.Email(value)  # Exceptions: EmailAlreadyExists, InvalidEmail
        self.set_value(value, "email")

    @property
    def profile_picture(self) -> str:
        """Profile picture property.

        :returns: user's profile picture in database

        """
        return self.get_value("profile_picture")

    @profile_picture.setter
    def profile_picture(self, filename: str) -> None:
        """Set new profile picture.

        :param str filename: Filename of the new profile picture

        """
        self.set_value(filename, "profile_picture")

    @property
    def profile_picture_path(self) -> str:
        """Profile picture path property.

        :returns: path to user's profile picture

        """
        return str(utl.ProfilePicture.get_profile_picture_path(self.profile_picture))

    @property
    def last_login_date(self) -> datetime:
        """Last login date property.

        :returns: last time the current account was accessed

        """
        return self.get_value("last_login_date")

    def update_last_login_date(self) -> None:
        """Set last login date."""
        self.set_value(datetime.now(), "last_login_date")

    @property
    def register_date(self) -> datetime:
        """Last login date property.

        :returns: register date of current user

        """
        return self.get_value("register_date")
