import os

import mysql.connector as mysql
from dotenv import load_dotenv

from lightning_pass.users.exceptions import AccountDoesNotExist

load_dotenv()
connection = mysql.connect(
    host=os.getenv("LOGINSDB_HOST"),
    user=os.getenv("LOGINSDB_USER"),
    password=os.getenv("LOGINSDB_PASS"),
    database=os.getenv("LOGINSDB_DB"),
)
cursor = connection.cursor()


# noinspection SqlInjection
class LoginUser:
    def __init__(self, username, password):
        """Constructor for user"""
        self.username = username
        self.password = password

    def __repr__(self):
        return f"Username = {self.username}, Password = {self.password}"

    def update_last_login_date(self):
        """update last login date whenever a user logs into their account."""
        sql = f"SELECT id FROM lightning_pass.credentials WHERE username = '{self.username}'"
        cursor.execute(sql)
        primary_key = cursor.fetchone()
        primary_key = int(primary_key[0])
        sql = f"UPDATE lightning_pass.credentials SET last_login_date = CURRENT_TIMESTAMP() WHERE id = {primary_key}"
        cursor.execute(sql)
        connection.commit()

    @staticmethod
    def check_details(username, password):
        """Check if login details match with a user in the database."""
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE (username, password) = ('{username}', '{password}')"
        cursor.execute(sql)
        row = cursor.fetchall()
        if len(row) <= 0:
            raise AccountDoesNotExist

    def log_in(self):
        """Validate login."""
        self.check_details(self.username, self.password)  # Expecting an exception here.
        self.update_last_login_date()
