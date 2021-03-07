import lightning_pass
from lightning_pass.users import utils


# noinspection SqlInjection
class Account:
    def __init__(self, user_id):
        """Constructor for account."""
        self.user_id = int(user_id)
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
        return f"Account({self.user_id})"

    @property
    def username(self):
        sql = (
            f"SELECT username FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        username = self.cursor.fetchone()[0]
        return username

    @username.setter
    def username(self, value):
        utils.check_username(value)
        sql = f"UPDATE lightning_pass.credentials SET username = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def password(self):
        sql = (
            f"SELECT password FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        password = self.cursor.fetchone()[0]
        return password

    @property
    def email(self):
        sql = f"SELECT email FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        email = self.cursor.fetchone()[0]
        return email

    @email.setter
    def email(self, value):
        utils.check_email(value)
        sql = f"UPDATE lightning_pass.credentials SET email = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture(self):
        sql = f"SELECT profile_picture FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        profile_picture = self.cursor.fetchone()[0]
        return profile_picture

    @profile_picture.setter
    def profile_picture(self, path):
        file = path
        sql = f"UPDATE lightning_pass.credentials SET profile_picture = '{file}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture_path(self):
        return str(utils.profile_picture_path(self.profile_picture))

    @property
    def last_login_date(self):
        sql = f"SELECT last_login_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        last_login_date = self.cursor.fetchone()[0]
        return last_login_date

    @property
    def register_date(self):
        sql = f"SELECT register_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        register_date = self.cursor.fetchone()[0]
        return register_date
