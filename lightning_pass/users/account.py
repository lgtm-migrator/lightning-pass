from __future__ import annotations

from datetime import datetime

from bcrypt import checkpw

from ..util.exceptions import AccountDoesNotExist
from ..util.utils import (
    Email,
    Password,
    ProfilePicture,
    Username,
    database_manager,
    get_user_id,
)


# noinspection SqlInjection
class Account:
    """The class hold information about currently logged in user.

    :param int user_id: User's id

    """

    def __init__(self, user_id: int = None) -> None:
        """Class contructor."""
        self.user_id = int(user_id) if user_id else None

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Account({self.user_id})"

    @classmethod
    def register(
        cls, username: str, password: bytes, confirm_password: str, email: str
    ) -> Account:
        """Secondary class constructor for register.

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
        Username(username)  # Exceptions: UsernameAlreadyExists, InvalidUsername
        Password(
            password, confirm_password
        )  # Exceptions: PasswordDoNotMatch, InvalidPassword
        Email(email)  # Exceptions: EmailAlreadyExists, Invalid email
        with database_manager() as db:
            sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
            val = [username, password, email]
            db.execute(sql, val)

        return cls(get_user_id(value=username, column="username"))

    @classmethod
    def login(cls, username: str, password: str) -> Account:
        """Secondary class constructor for login.
        Updates last_login_date if log in is successful.

        :param str username: User's username
        :param str password: User's password

        :returns: Account object instantiated with current user id

        :raises AccountDoesNotExist: if username wasn't found in the database
        :raises AccountDoesNotExist: if password doesn't match with the hashed password in the database

        """
        with database_manager() as db:
            sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
            result = db.execute(sql)

        try:
            result.fetchone()
        except AttributeError:
            raise AccountDoesNotExist

        user_id = get_user_id(value=username, column="username")
        with database_manager() as db:
            sql = (
                f"SELECT password FROM lightning_pass.credentials WHERE id = {user_id}"
            )
            result = db.execute(sql)

        if not checkpw(password.encode("utf-8"), result.fetchone()[0].encode("utf-8")):
            raise AccountDoesNotExist
        else:
            account = cls(user_id)
            account.update_last_login_date()
            return account

    @property
    def username(self) -> str:
        """Username property.

        :returns: user's username in database

        """
        with database_manager() as db:
            sql = f"SELECT username FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)

        return result.fetchone()[0]

    @username.setter
    def username(self, value: str) -> None:
        """Set new username.

        :param str value: New username

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern

        """
        Username(value)  # Exceptions: UsernameAlreadyExists, InvalidUsername
        with database_manager() as db:
            sql = f"UPDATE lightning_pass.credentials SET username = '{value}' WHERE id = {self.user_id}"
            db.execute(sql)

    @property
    def password(self) -> str:
        """Password property.

        :returns: user's password in database

        """
        with database_manager() as db:
            sql = f"SELECT password FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)
        password = result.fetchone()[0]

        return password

    @property
    def email(self) -> None:
        """Email property.

        :returns: user's email in database

        """
        with database_manager() as db:
            sql = f"SELECT email FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)

        return result.fetchone()[0]

    @email.setter
    def email(self, value: str) -> None:
        """Set new email.

        :param str value: New email

        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        Email(value)  # Exceptions: EmailAlreadyExists, InvalidEmail
        with database_manager() as db:
            sql = f"UPDATE lightning_pass.credentials SET email = '{value}' WHERE id = {self.user_id}"
            db.execute(sql)

    @property
    def profile_picture(self) -> str:
        """Profile picture property.

        :returns: user's profile picture in database

        """
        with database_manager() as db:
            sql = f"SELECT profile_picture FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)

        return result.fetchone()[0]

    @profile_picture.setter
    def profile_picture(self, filename: str) -> None:
        """Set new profile picture.

        :param str filename: Filename of the new profile picture

        """
        with database_manager() as db:
            sql = f"UPDATE lightning_pass.credentials SET profile_picture = '{filename}' WHERE id = {self.user_id}"
            db.execute(sql)

    @property
    def profile_picture_path(self) -> str:
        """Profile picture path property.

        :returns: path to user's profile picture

        """
        path = str(ProfilePicture.get_profile_picture_path(self.profile_picture))
        return path

    @property
    def last_login_date(self) -> datetime:
        """Last login date property.

        :returns: last time the current account was accessed

        """
        with database_manager() as db:
            sql = f"SELECT last_login_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)

        return result.fetchone()[0]

    def update_last_login_date(self) -> None:
        """Set last login date."""
        with database_manager() as db:
            sql = (
                f"UPDATE lightning_pass.credentials SET last_login_date = CURRENT_TIMESTAMP()"
                f"WHERE id = {self.user_id}"
            )
            db.execute(sql)

    @property
    def register_date(self) -> datetime:
        """Last login date property.

        :returns: register date of current user

        """
        with database_manager() as db:
            sql = f"SELECT register_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
            result = db.execute(sql)

        return result.fetchone()[0]
