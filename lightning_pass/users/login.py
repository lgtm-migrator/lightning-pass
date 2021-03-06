import lightning_pass
from lightning_pass.users.exceptions import Exceptions as Exc


# noinspection SqlInjection
class LoginUser:
    def __init__(self, username, password):
        """Constructor for user"""
        self.username = username
        self.password = password
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
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
        """Check if login details match with a user in the database."""
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE (username, password) = ('{username}', '{password}')"
        cursor.execute(sql)
        row = cursor.fetchall()
        if len(row) <= 0:
            raise Exc.AccountDoesNotExist

    def log_in(self):
        """Validate login."""
        self.check_details(
            self.cursor, self.username, self.password
        )  # Expecting an exception here.
        self.update_last_login_date()
