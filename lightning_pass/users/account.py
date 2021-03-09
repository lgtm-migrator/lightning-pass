from datetime import datetime

from bcrypt import checkpw

import lightning_pass
from lightning_pass.util.exceptions import AccountDoesNotExist
from lightning_pass.util.utils import (
    check_email,
    check_password,
    check_username,
    get_user_id,
    hash_password,
    profile_picture_path,
)


# noinspection SqlInjection
class Account:
    """The class hold information about currently logged in user.

    :param int user_id: user's id

    """

    cursor, connection = lightning_pass.connect_to_database()

    def __init__(self, user_id: int = None) -> None:
        """Class contructor."""
        self.user_id = int(user_id) if user_id else None

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Account({self.user_id})"

    @classmethod
    def register(
        cls, username: str, password: str, confirm_password: str, email: str
    ) -> "Account":
        """Secondary class constructor for register.

        :param str username: user's username
        :param str password: user's password
        :param str confirm_password: user's confirmed password
        :param str email: user's email

        :raises UsernameAlreadyExists: If username is already registered in the database.
        :raises InvalidUsername: If username doesn't match the required pattern.
        :raises PasswordDoNotMatch: If password and confirm_password are not the same.
        :raises InvalidPassword: If password doesn't match the required pattern.
        :raises EmailAlreadyExists: If email is already registered in the database.
        :raises InvalidEmail: If email doesn't match the email pattern.

        :returns account: Account object instantiated with current user id
        :rtype Account

        """
        check_username(username)  # Exceptions: UsernameAlreadyExists, InvalidUsername
        check_password(
            password, confirm_password
        )  # Exceptions: PasswordDoNotMatch, InvalidPassword
        check_email(email)  # Exceptions: EmailAlreadyExists, Invalid email

        sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
        val = [username, hash_password(password), email]
        cls.cursor.execute(sql, val)
        cls.connection.commit()

        return cls(get_user_id(value=username, column="username"))

    @classmethod
    def login(cls, username: str, password: str) -> "Account":
        """Secondary class constructor for login.
        Updates last_login_date if log in is successful.

        :param str username: user's username
        :param str password: user's password

        :raises AccountDoesNotExist: If username wasn't found in the database.
        :raises AccountDoesNotExist: If password doesn't match with the hashed password in the database.

        :returns account: Account object instantiated with current user id
        :rtype Account

        """
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
        cls.cursor.execute(sql)
        row = cls.cursor.fetchone()
        if row is None:
            raise AccountDoesNotExist
        user_id = get_user_id(value=username, column="username")
        sql = f"SELECT password FROM lightning_pass.credentials WHERE id = {user_id}"
        cls.cursor.execute(sql)
        hashed_password = cls.cursor.fetchone()
        if not checkpw(password.encode("utf-8"), hashed_password[0].encode("utf-8")):
            raise AccountDoesNotExist
        else:
            account = cls(user_id)
            account.update_last_login_date()
            return account

    @property
    def username(self) -> str:
        """Username property.

        :returns username: user's username in database
        :rtype str

        """
        sql = (
            f"SELECT username FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        username = self.cursor.fetchone()[0]
        return username

    @username.setter
    def username(self, value: str) -> None:
        """Username setter

        :param str value: new username

        """
        check_username(value)
        sql = f"UPDATE lightning_pass.credentials SET username = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def password(self) -> str:
        """Password property.

        :returns password: user's password in database
        :rtype str

        """
        sql = (
            f"SELECT password FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        password = self.cursor.fetchone()[0]
        return password

    @property
    def email(self) -> None:
        """Email property.

        :returns email: user's email in database
        :rtype str

        """
        sql = f"SELECT email FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        email = self.cursor.fetchone()[0]
        return email

    @email.setter
    def email(self, value: str) -> None:
        """Email setter.

        :param str value: new email

        """
        check_email(value)
        sql = f"UPDATE lightning_pass.credentials SET email = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture(self) -> str:
        """Profile picture property.

        :return: profile_picture: user's profile picture in database
        :rtype str

        """
        sql = f"SELECT profile_picture FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        profile_picture = self.cursor.fetchone()[0]
        return profile_picture

    @profile_picture.setter
    def profile_picture(self, filename: str) -> None:
        """Profile picture setter.

        :param str filename: filename of the new profile picture

        """
        sql = f"UPDATE lightning_pass.credentials SET profile_picture = '{filename}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture_path(self) -> str:
        """Profile pictue path property.

        :returns path: path to user's profile picture
        :rtype str

        """
        path = str(profile_picture_path(self.profile_picture))
        return path

    @property
    def last_login_date(self) -> datetime:
        """Last login date property.

        :returns last_login_date: last time the current account was accessed
        :rtype datetime.datetime

        """
        sql = f"SELECT last_login_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        last_login_date = self.cursor.fetchone()[0]
        return last_login_date

    def update_last_login_date(self) -> None:
        """Last login date setter. """
        sql = f"UPDATE lightning_pass.credentials SET last_login_date = CURRENT_TIMESTAMP() WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def register_date(self) -> None:
        """Last login date property.

        :returns register_date: register date of current user
        :rtype datetime.datetime

        """
        sql = f"SELECT register_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        register_date = self.cursor.fetchone()[0]
        return register_date
