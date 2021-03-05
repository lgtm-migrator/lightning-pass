import os
import re
from secrets import compare_digest

import mysql.connector as mysql
from dotenv import load_dotenv

from lightning_pass.users.exceptions import (
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

load_dotenv()
connection = mysql.connect(
    host=os.getenv("LOGINSDB_HOST"),
    user=os.getenv("LOGINSDB_USER"),
    password=os.getenv("LOGINSDB_PASS"),
    database=os.getenv("LOGINSDB_DB"),
)
cursor = connection.cursor()


# noinspection SqlInjection
class RegisterUser:
    def __init__(self, username, password, confirm_password, email):
        """Constructor for user"""
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.email = email

    @staticmethod
    def check_username(username):
        """Check whether a username already exists in a database and if it matches a required pattern."""
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
        cursor.execute(sql)
        row = cursor.fetchall()

        if not len(row) <= 0:
            raise UsernameAlreadyExists
        elif len(username) < 5:
            raise InvalidUsername

    @staticmethod
    def check_password(password, confirm_password):
        if (
            len(password) < 8
            or len(re.findall(r"[A-Z]", password)) <= 0
            or len(re.findall(r"[0-9~!@#$%^&*()_+/\[\]{}:'\"<>?|;-\\]", password)) <= 0
        ):
            raise InvalidPassword
        elif not compare_digest(password, confirm_password):
            raise PasswordsDoNotMatch

    @staticmethod
    def check_email(email):
        """Check whether an email already exists and if it matches a correct email pattern."""
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
        cursor.execute(sql)
        row = cursor.fetchall()

        if not len(row) <= 0:
            raise EmailAlreadyExists
        elif not re.search(REGEX_EMAIL, email):
            raise InvalidEmail

    def credentials_eligibility(self):
        """Used to check whether submitted credentials meet the desired requirements."""
        self.check_username(self.username)
        self.check_password(self.password, self.confirm_password)
        self.check_email(self.email)

    def insert_into_db(self):
        """Insert user into a database.
        If credentials check fails, a custom exception is raised."""
        self.credentials_eligibility()  # Exception expected here
        sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
        val = [self.username, self.password, self.email]
        cursor.execute(sql, val)
        connection.commit()
