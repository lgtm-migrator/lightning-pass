import os

import mysql.connector as mysql
from dotenv import load_dotenv

from lightning_pass.users.register import RegisterUser

load_dotenv()
connection = mysql.connect(
    host=os.getenv("LOGINSDB_HOST"),
    user=os.getenv("LOGINSDB_USER"),
    password=os.getenv("LOGINSDB_PASS"),
    database=os.getenv("LOGINSDB_DB"),
)
cursor = connection.cursor()


# noinspection SqlInjection
class Account:
    def __init__(self, user_id):
        """Constructor for account."""
        self.user_id = int(user_id)

    @property
    def username(self):
        sql = f"SELECT username FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        cursor.execute(sql)
        username = cursor.fetchone()[0]
        return username

    @property
    def password(self):
        sql = f"SELECT password FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        cursor.execute(sql)
        password = cursor.fetchone()[0]
        return password

    @property
    def email(self):
        sql = (
            f"SELECT email FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        )
        cursor.execute(sql)
        email = cursor.fetchone()[0]
        return email

    @property
    def profile_picture(self):
        sql = f"SELECT profile_picture FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        cursor.execute(sql)
        profile_picture = cursor.fetchone()[0]
        return profile_picture

    @property
    def last_login_date(self):
        sql = f"SELECT last_login_date FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        cursor.execute(sql)
        last_login_date = cursor.fetchone()[0]
        return last_login_date

    @property
    def register_date(self):
        sql = f"SELECT register_date FROM lightning_pass.credentials WHERE id = '{self.user_id}'"
        cursor.execute(sql)
        register_date = cursor.fetchone()[0]
        return register_date

    @username.setter
    def username(self, value):
        RegisterUser.check_username(value)
        sql = f"UPDATE lightning_pass.credentials SET username = '{value}' WHERE id = {self.user_id}"
        cursor.execute(sql)
        connection.commit()

    @email.setter
    def email(self, value):
        RegisterUser.check_email(value)
        sql = f"UPDATE lightning_pass.credentials SET email = '{value}' WHERE id = {self.user_id}"
        cursor.execute(sql)
        connection.commit()

    @profile_picture.setter
    def profile_picture(self, path):
        file = path
        sql = f"UPDATE lightning_pass.credentials SET profile_picture = '{file}' WHERE id = {self.user_id}"
        cursor.execute(sql)
        connection.commit()
