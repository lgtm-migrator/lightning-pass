import lightning_pass
from lightning_pass.util.utils import check_email, check_username, profile_picture_path


# noinspection SqlInjection
class Account:
    """The class hold information about currently logged in user.

    :param int user_id: user's id

    """

    def __init__(self, user_id):
        """Class contructor."""
        self.user_id = int(user_id)
        self.cursor, self.connection = lightning_pass.connect_to_database()

    def __repr__(self):
        """Provide information about this class."""
        return f"Account({self.user_id})"

    @property
    def username(self):
        """Username property.

        :returns username: user's username in database
        :rtype str

        """
        sql = (
            f"SELECT username FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        username = self.cursor.fetchone()[0]
        return username

    @username.setter
    def username(self, value):
        """Username setter

        :param str value: new username

        """
        check_username(value)
        sql = f"UPDATE lightning_pass.credentials SET username = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def password(self):
        """Password property.

        :returns password: user's password in database
        :rtype str

        """
        sql = (
            f"SELECT password FROM lightning_pass.credentials WHERE id = {self.user_id}"
        )
        self.cursor.execute(sql)
        password = self.cursor.fetchone()[0]
        return password

    @property
    def email(self):
        """Email property.

        :returns email: user's email in database
        :rtype str

        """
        sql = f"SELECT email FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        email = self.cursor.fetchone()[0]
        return email

    @email.setter
    def email(self, value):
        """Email setter.

        :param str value: new email

        """
        check_email(value)
        sql = f"UPDATE lightning_pass.credentials SET email = '{value}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture(self):
        """Profile picture property.

        :return: profile_picture: user's profile picture in database
        :rtype str

        """
        sql = f"SELECT profile_picture FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        profile_picture = self.cursor.fetchone()[0]
        return profile_picture

    @profile_picture.setter
    def profile_picture(self, filename):
        """Profile picture setter.

        :param str filename: filename of the new profile picture.

        """
        sql = f"UPDATE lightning_pass.credentials SET profile_picture = '{filename}' WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        self.connection.commit()

    @property
    def profile_picture_path(self):
        """Profile pictue path property.

        :returns path: path to user's profile picture
        :rtype str

        """
        path = str(profile_picture_path(self.profile_picture))
        return path

    @property
    def last_login_date(self):
        """Last login date property.

        :returns last_login_date: last time the current account was accessed
        :rtype datetime.datetime

        """
        sql = f"SELECT last_login_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        last_login_date = self.cursor.fetchone()[0]
        return last_login_date

    @property
    def register_date(self):
        """Last login date property.

        :returns register_date: register date of current user
        :rtype datetime.datetime

        """
        sql = f"SELECT register_date FROM lightning_pass.credentials WHERE id = {self.user_id}"
        self.cursor.execute(sql)
        register_date = self.cursor.fetchone()[0]
        return register_date
