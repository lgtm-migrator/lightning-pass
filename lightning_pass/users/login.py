from bcrypt import checkpw

import lightning_pass
from lightning_pass.util.exceptions import AccountDoesNotExist
from lightning_pass.util.utils import get_user_id


# noinspection SqlInjection
class LoginUser:
    """The LoginUser object contains the log in functionality.

    :param str username: user's username
    :param str password: user's password

    """

    def __init__(self, username, password):
        """Class constructor."""
        self.username = username
        self.password = password
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
        """Provide information about this class."""
        return f"LoginUser({self.username}, {self.password})"

    def update_last_login_date(self):
        """Update last login date whenever a user logs into their account."""
        sql = f"SELECT id FROM lightning_pass.credentials WHERE username = '{self.username}'"
        self.cursor.execute(sql)
        primary_key = self.cursor.fetchone()
        primary_key = int(primary_key[0])
        sql = f"UPDATE lightning_pass.credentials SET last_login_date = CURRENT_TIMESTAMP() WHERE id = {primary_key}"
        self.cursor.execute(sql)
        self.connection.commit()

    @staticmethod
    def check_details(cursor, username, password):
        """Check if login details match with a user in the database.

        :param MySQLCursor cursor: Database connection cursor.
        :param str username: user's username
        :param str password: user's password

        :raises AccountDoesNotExist: If username wasn't found in the database.
        :raises AccountDoesNotExist: If password doesn't match with the hashed password in the database.

        """
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
        cursor.execute(sql)
        row = cursor.fetchone()
        try:
            if len(row) <= 0:
                raise AccountDoesNotExist
        except TypeError:
            raise AccountDoesNotExist
        user_id = get_user_id(username, "username")
        sql = f"SELECT password FROM lightning_pass.credentials WHERE id = {user_id}"
        cursor.execute(sql)
        hashed_password = cursor.fetchone()
        try:
            if not checkpw(
                password.encode("utf-8"), hashed_password[0].encode("utf-8")
            ):
                raise AccountDoesNotExist
        except TypeError:
            raise AccountDoesNotExist

    def log_in(self):
        """Validate login.

        :raises: Refer to the called functions to see all of the possible Exceptions.

        """
        self.check_details(self.cursor, self.username, self.password)
        self.update_last_login_date()
