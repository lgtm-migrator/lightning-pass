import os

import mysql.connector as mysql
from dotenv import load_dotenv

load_dotenv()
connection = mysql.connect(
    host=os.getenv("LOGINSDB_HOST"),
    user=os.getenv("LOGINSDB_USER"),
    password=os.getenv("LOGINSDB_PASS"),
    database=os.getenv("LOGINSDB_DB"),
)
cursor = connection.cursor()


class LoginUser:
    def __init__(self, username, password):
        """ Constructor for user. """
        self.username = username
        self.password = password

    def check_username(self):
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{self.username}'"
        cursor.execute(sql)
        row = cursor.fetchall()
        if len(row) < 1:
            return True
        else:
            return False

    def log_in(self):
        """ Validate login. """
        ...


user = LoginUser("usernam", "password")
user.check_username()
