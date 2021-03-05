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


def get_user_id(value, column):
    """Return user id from any user detail and its column."""
    sql = f"SELECT id FROM lightning_pass.credentials WHERE {column} = '{value}'"
    cursor.execute(sql)
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return False
