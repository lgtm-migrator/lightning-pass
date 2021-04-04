"""Module containing the Account class and other functions related to accounts."""
from __future__ import annotations

import functools
from datetime import datetime
from typing import Optional, Union, Generator

import lightning_pass.util.credentials as credentials
import lightning_pass.util.database as database
from lightning_pass.util.exceptions import AccountDoesNotExist
from lightning_pass.users.vaults import Vault


def change_password(user_id: int, password: str, confirm_password: str) -> None:
    """Check eligibility of new passwords and possibly change the password.

    :raises InvalidPassword: if the passwords do not match the required pattern.
    :raises PasswordsDoNotMatch: if password and confirm_password are not the same.

    """
    # Exceptions: InvalidPassword, PasswordsDoNotMatch
    credentials.Password(password, confirm_password).__call__()
    credentials.set_user_item(
        user_id,
        "id",
        credentials.Password.hash_password(password),
        "password",
    )


class Account:
    """This class holds information about the currently logged in user."""

    last_login_date: datetime

    def __init__(self, user_id: Optional[int] = None) -> None:
        """Construct the class.

        :param int user_id: User's id, defaults to None

        """
        self.user_id = int(user_id)
        self.vault_unlocked = False

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Account({self.user_id})"

    @classmethod
    def register(
        cls,
        username: str,
        password: str,
        confirm_password: str,
        email: str,
    ) -> Account:
        """Secondary class constructor for registering.

        :param str username: User's username
        :param str password: User's password
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
        # Exceptions: UsernameAlreadyExists, InvalidUsername
        credentials.Username(username)(should_exist=False)
        # Exceptions: PasswordDoNotMatch, InvalidPassword
        credentials.Password(
            password,
            confirm_password,
        )()
        # Exceptions: EmailAlreadyExists, Invalid email
        credentials.Email(email)()

        # no exceptions raised -> insert into db
        with database.database_manager() as db:
            sql = (
                "INSERT INTO lightning_pass.credentials (username, password, email)"
                "     VALUES (%s, %s, %s)"
            )
            val = (username, credentials.Password.hash_password(password), email)
            db.execute(sql, val)

        return cls(credentials.get_user_item(username, "username", "id"))

    @classmethod
    def login(cls, username: str, password: str) -> Account:
        """Secondary class constructor for log in.

        Stores old last login date and updates new last login date

        :param str username: User's username
        :param str password: User's password

        :returns: Account object instantiated with current user id

        :raises AccountDoesNotExist: if username wasn't found in the database
        :raises AccountDoesNotExist: if password doesn't match with the hashed password in the database

        """
        if not credentials.Username.check_username_existence(
            username,
            should_exist=True,
        ):
            raise AccountDoesNotExist

        if not credentials.Password.authenticate_password(
            password,
            credentials.get_user_item(username, "username", "password"),
        ):
            raise AccountDoesNotExist

        account = cls(credentials.get_user_item(username, "username", "id"))
        account.last_login_date = account._last_login_date
        account.update_last_login_date()

        return account

    def get_value(self, result_column: str) -> Union[str, datetime]:
        """Simplify getting user values.

        :param str result_column: Column from which we're collecting the value

        :returns: the result value

        """
        return credentials.get_user_item(self.user_id, "id", result_column)

    def set_value(
        self, result: Union[int, str, bytes, datetime], result_column: str
    ) -> None:
        """Simplify setting user values.

        :param str result: Value which we're inserting
        :param str result_column: Column where to insert the value

        """
        credentials.set_user_item(self.user_id, "id", result, result_column)

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
        # Exceptions: UsernameAlreadyExists, InvalidUsername
        credentials.Username(value)(should_exist=False)
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
        # Exceptions: EmailAlreadyExists, InvalidEmail
        credentials.Email(value)()
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
        return str(
            credentials.ProfilePicture.get_profile_picture_path(self.profile_picture)
        )

    @property
    def _last_login_date(self) -> datetime:
        """Last login date property.

        :returns: last time the current account was accessed

        """
        return self.get_value("last_login_date")

    def update_last_login_date(self) -> None:
        """Set last login date."""
        with database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """UPDATE lightning_pass.credentials
                        SET last_login_date = CURRENT_TIMESTAMP()
                      WHERE id = %s""" % (
                "%s",
            )
            # expecting a sequence thus val has to be a tuple (created by the trailing comma)
            db.execute(sql, (self.user_id,))

    @functools.cached_property
    def register_date(self) -> datetime:
        """Last login date property.

        Lru caching the register date to avoid unnecessary database queries,
        (register_date needs to be collected only once, it is not possible to change it.)

        :returns: register date of current user

        """
        return self.get_value("register_date")

    @property
    def master_password(self) -> str:
        """Return current master password."""
        return self.get_value("master_password")

    @master_password.setter
    def master_password(self, password_information: tuple[str, str, str]) -> None:
        """Set a new master password.

        :param password_information:
            index 0: Current normal password, used to check account ownership
            index 1: New master password
            index 2: Second master password, used to check that the new passwords match

        :raises AccountDoesNotExist: if the normal password is not correct
        :raises PasswordsDoNotMatch: if the master passwords do not match
        :raises InvalidPassword: if the master password doesn't meet the required pattern

        """
        if not credentials.Password.authenticate_password(
            password_information[0], self.password
        ):
            raise AccountDoesNotExist

        # Exceptions: InvalidPassword, PasswordsDoNotMatch
        credentials.Password(
            password_information[1],
            password_information[2],
        )()

        self.set_value(
            credentials.Password.hash_password(password_information[1]),
            "master_password",
        )

    @property
    def vault_pages(self) -> Generator:
        """Yield registered vault pages tied to the current account."""
        with database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """SELECT *
                       FROM lightning_pass.vaults
                      WHERE user_id = %s""" % (
                "%s",
            )
            # expecting a sequence thus val has to be a tuple (created by the trailing comma)
            db.execute(sql, (self.user_id,))
            result = db.fetchall()

        # list slice first element -> database primary key
        yield from (Vault(*vault[1:]) for vault in result if vault)

    @property
    def vault_pages_int(self) -> int:
        """Return an integer with the amount of vault pages a user has registered."""
        return sum(1 for _ in self.vault_pages)


__all__ = ["Account"]
