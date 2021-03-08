import lightning_pass
from lightning_pass.util.utils import (
    check_email,
    check_password,
    check_username,
    hash_password,
)


# noinspection SqlInjection
class RegisterUser:
    """The RegisterUser object contains functionality for inserting new users into the database.

    :param str username: user's username
    :param str password: user's password
    :param str confirm_password: user's confirmation password
    :param str email: user's email

    """

    def __init__(self, username, password, confirm_password, email):
        """Class constructor."""
        self.username = username
        self.password = password
        self.hashed_password = hash_password(self.password)
        self.confirm_password = confirm_password
        self.email = email
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
        """Provide information about this class."""
        return f"RegisterUser({self.username}, {self.password}, {self.confirm_password}, {self.email})"

    def credentials_eligibility(self):
        """Check whether submitted credentials meet the desired requirements.

        :raises: Refer to the called functions to see all of the possible Exceptions.

        """
        check_username(self.username)
        check_password(self.password, self.confirm_password)
        check_email(self.email)

    def insert_into_db(self):
        """Insert a user into the database."""
        self.credentials_eligibility()
        sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
        val = [self.username, self.hashed_password, self.email]
        self.cursor.execute(sql, val)
        self.connection.commit()
