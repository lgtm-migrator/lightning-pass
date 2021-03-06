import lightning_pass
from lightning_pass.users import utils


# noinspection SqlInjection
class RegisterUser:
    def __init__(self, username, password, confirm_password, email):
        """Constructor for user"""
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.email = email
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
        return f"RegisterUser({self.username}, {self.password}, {self.confirm_password}, {self.email})"

    def credentials_eligibility(self):
        """Used to check whether submitted credentials meet the desired requirements."""
        utils.check_username(self.username)
        utils.check_password(self.password, self.confirm_password)
        utils.check_email(self.email)

    def insert_into_db(self):
        """Insert user into a database. If credentials check fails, a custom exception is raised."""
        self.credentials_eligibility()  # Exception expected here
        sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
        val = [self.username, self.password, self.email]
        self.cursor.execute(sql, val)
        self.connection.commit()
