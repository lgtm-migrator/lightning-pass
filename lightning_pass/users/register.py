import os
import re

import mysql.connector as mysql
from dotenv import load_dotenv

REGEX_EMAIL = r"^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

load_dotenv()
connection = mysql.connect(
    host=os.getenv("LOGINSDB_HOST"),
    user=os.getenv("LOGINSDB_USER"),
    password=os.getenv("LOGINSDB_PASS"),
    database=os.getenv("LOGINSDB_DB"),
)
cursor = connection.cursor()


class RegisterUser:
    def __init__(
        self,
        username,
        password,
        email,
    ):
        """ Constructor for user. """
        self.username = username
        self.password = password
        self.email = email

    @staticmethod
    def check_username(username):
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE username = '{username}'"
        cursor.execute(sql)
        row = cursor.fetchall()
        if len(row) < 1:
            return True
        else:
            return False

    @staticmethod
    def check_email(email):
        sql = f"SELECT 1 FROM lightning_pass.credentials WHERE email = '{email}'"
        cursor.execute(sql)
        row = cursor.fetchall()
        if len(row) < 1:
            return True
        else:
            return False

    def credentials_eligibility(self):
        """ Used to check whether submitted credentials meet the desired requirements. """
        if (
            not re.search(REGEX_EMAIL, self.email)
            or not len(re.findall('[0-9/.,*+-`"a-zA-Z]', self.username)) > 5
            or not len(re.findall("[A-Z]", self.password)) != 0
            or not len(re.findall('[0-9/.,*+-`"]', self.password)) != 0
            or not len(re.findall('[0-9/.,*+-`"a-zA-Z]', self.password)) > 8
        ):
            print("false")
            return False
        else:
            if not self.check_username(self.username):
                return "username exists"
            elif not self.check_email(self.email):
                return "email exists"
            else:
                return True

    def insert_into_db(self):
        if self.credentials_eligibility():
            sql = "INSERT INTO lightning_pass.credentials (username, password, email) VALUES (%s, %s, %s)"
            val = [self.username, self.password, self.email]
            cursor.execute(sql, val)
            connection.commit()
        else:
            return False


user = RegisterUser("usernam", "passwordLL12", "emai@email.com")
user.insert_into_db()
