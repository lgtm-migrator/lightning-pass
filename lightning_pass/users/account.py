"""Module containing the Account class and other functions related to accounts."""
from __future__ import annotations

import functools
from datetime import datetime
from typing import TYPE_CHECKING, Generator, Optional, TypeVar, Union

import lightning_pass.users.password_hashing as pwd_hashing
import lightning_pass.users.vaults as vaults
import lightning_pass.util.credentials as credentials
import lightning_pass.util.database as database
from lightning_pass.util.exceptions import (
    AccountDoesNotExist,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
    ValidationFailure,
)
from lightning_pass.util.validators import (
    EmailValidator,
    PasswordValidator,
    UsernameValidator,
    Validator,
)

if TYPE_CHECKING:
    from lightning_pass.users.password_hashing import HashedVaultCredentials
    from lightning_pass.users.vaults import Vault
    from lightning_pass.util.credentials import PasswordData


_V = TypeVar("_V", bound=Validator)


class Account:
    """This class holds information about the currently logged in user."""

    credentials = credentials
    database = database
    pwd_hashing = pwd_hashing
    vaults = vaults

    username_validator: _V = UsernameValidator()
    password_validator: _V = PasswordValidator()
    email_validator: _V = EmailValidator()

    def __init__(self, user_id: int) -> None:
        """Construct the class.

        :param int user_id: Database primary key ``id`` of the account

        """
        self._user_id = user_id

        self._current_login_date = self.get_value("last_login_date")

        self._vault_unlocked = False
        self._current_vault_unlock_date = self.get_value("last_vault_unlock_date")

        self._master_key_str = ""

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.user_id})"

    def __bool__(self):
        return bool(self.get_value("id"))

    @classmethod
    def register(
        cls,
        username: str,
        password: str,
        confirm_password: str,
        email: str,
    ) -> Account:
        """Secondary class constructor for registering.

        :param str username: User's username
        :param str password: User's password
        :param str confirm_password: User's confirmed password
        :param str email: User's email

        :returns: Account object instantiated with current user id

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern
        :raises PasswordDoNotMatch: if password and confirm_password are not the same
        :raises InvalidPassword: if password doesn't match the required pattern
        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        checks = {
            functools.partial(
                cls.username_validator.unique,
                username,
            ): UsernameAlreadyExists,
            functools.partial(
                cls.username_validator.pattern,
                username,
            ): InvalidUsername,
            functools.partial(
                cls.password_validator.pattern,
                password,
            ): InvalidPassword,
            functools.partial(
                cls.password_validator.match,
                password,
                confirm_password,
            ): PasswordsDoNotMatch,
            functools.partial(cls.email_validator.unique, email): EmailAlreadyExists,
            functools.partial(cls.email_validator.pattern, email): InvalidEmail,
        }

        for func, exc in checks.items():
            try:
                func()
            except ValidationFailure:
                raise exc

        with cls.database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """INSERT INTO lightning_pass.credentials (username, password, email)
                          VALUES ({},{},{})""".format(
                "%s",
                "%s",
                "%s",
            )
            db.execute(sql, (username, cls.pwd_hashing.hash_password(password), email))

        return cls(cls.credentials.get_user_item(username, "username", "id"))

    @classmethod
    def login(cls, username: str, password: str) -> Account:
        """Secondary class constructor for log in.

        Stores old last login date and updates new last login date

        :param username: User's username
        :param password: User's password

        :returns: ``Account`` object instantiated with current user id

        :raises AccountDoesNotExist: if username wasn't found in the database
        :raises AccountDoesNotExist: if password doesn't match with the hashed password in the database

        """
        try:
            cls.username_validator.unique(username, should_exist=True)
            cls.password_validator.authenticate(
                password,
                cls.credentials.get_user_item(
                    username,
                    "username",
                    "password",
                ),
            )
        except ValidationFailure:
            raise AccountDoesNotExist

        account = cls(cls.credentials.get_user_item(username, "username", "id"))
        account._current_login_date = account.get_value("last_login_date")
        account.update_date("last_login_date")
        return account

    def get_value(self, result_column: str) -> Union[str, bytes, datetime]:
        """Simplify getting user values.

        :param str result_column: Column from which we're collecting the value

        :returns: the result value

        """
        return self.credentials.get_user_item(self.user_id, "id", result_column)

    def set_value(
        self,
        result: Union[int, str, bytes, datetime],
        result_column: str,
    ) -> None:
        """Simplify setting user values.

        :param str result: Value which we're inserting
        :param str result_column: Column where to insert the value

        """
        self.credentials.set_user_item(self.user_id, "id", result, result_column)

    def validate_password_data(self, data: PasswordData) -> None:
        """Validate given password data container.

        Used when validating master password or new account password.
        Both of these operations use the same data containers.

        :param data: The data container

        :raises AccountDoesNotExist: If the authentication fails
        :raises InvalidPassword: If the new password doesn't match the required pattern
            Uses the validator of the current account
        :raises PasswordsDoNotMatch: If the passwords do not match

        """
        checks = {
            functools.partial(
                self.password_validator.authenticate,
                data.confirm_previous,
                self.password,
            ): AccountDoesNotExist,
            functools.partial(
                self.password_validator.pattern,
                data.new_password,
            ): InvalidPassword,
            functools.partial(
                self.password_validator.match,
                data.new_password,
                data.confirm_new,
            ): PasswordsDoNotMatch,
        }

        for func, exc in checks.items():
            try:
                func()
            except ValidationFailure:
                raise exc

    def update_date(self, column: str) -> None:
        """Update database TIMESTAMP column with CURRENT_TIMESTAMP().

        Used for last_login_date and last_vault_unlock_date.

        :param column: Which column to update

        """
        with self.database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """UPDATE lightning_pass.credentials
                        SET {} = CURRENT_TIMESTAMP()
                      WHERE id = {}""".format(
                column,
                "%s",
            )
            # expecting a sequence thus val has to be a tuple (created by the trailing comma)
            db.execute(sql, (self.user_id,))

    @property
    def user_id(self):
        """Return database ID of the current account."""
        return self._user_id

    @property
    def username(self) -> str:
        """Username property.

        :returns: user's username in database

        """
        return self.get_value("username")

    @username.setter
    def username(self, value: str) -> None:
        """Set new username.

        :param str value: New username

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern

        """
        checks = {
            functools.partial(self.username_validator.pattern, value): InvalidUsername,
            functools.partial(
                self.username_validator.unique,
                value,
            ): UsernameAlreadyExists,
        }

        for func, exc in checks.items():
            try:
                func()
            except ValidationFailure:
                raise exc

        self.set_value(value, "username")

    @property
    def password(self) -> bytes:
        """Password property.

        :returns: user's password in database

        """
        return self.get_value("password")

    @password.setter
    def password(self, data: PasswordData) -> None:
        """Password setter.

        :param data: The data container with all the necessary details.

        """
        self.validate_password_data(data)

        self.set_value(
            self.pwd_hashing.hash_password(str(data.new_password)),
            "password",
        )

    def reset_password(self, password: str, confirm_password: str) -> None:
        """Reset user's password."""
        try:
            self.password_validator.pattern(password)
        except ValidationFailure:
            raise InvalidPassword
        try:
            self.password_validator.match(password, confirm_password)
        except ValidationFailure:
            raise PasswordsDoNotMatch

        self.set_value(self.pwd_hashing.hash_password(password), "password")

    @property
    def email(self) -> str:
        """Email property.

        :returns: user's email in database

        """
        return self.get_value("email")

    @email.setter
    def email(self, value: str) -> None:
        """Set new email.

        :param str value: New email

        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        try:
            self.email_validator.pattern(value)
        except ValidationFailure:
            raise InvalidEmail
        try:
            self.email_validator.unique(value)
        except ValidationFailure:
            raise EmailAlreadyExists

        self.set_value(value, "email")

    @property
    def profile_picture(self) -> str:
        """Profile picture property.

        :returns: user's profile picture in database

        """
        return self.get_value("profile_picture")

    @profile_picture.setter
    def profile_picture(self, filename: str) -> None:
        """Set new profile picture.

        :param filename: Filename of the new profile picture

        """
        self.set_value(filename, "profile_picture")

    @property
    def profile_picture_path(self) -> str:
        """Profile picture path property.

        :returns: path to user's profile picture

        """
        return str(self.credentials.get_profile_picture_path(self.profile_picture))

    @property
    def current_login_date(self) -> datetime:
        """Return the 'previous' date when the current user has been logged in."""
        return self._current_login_date

    @functools.cached_property
    def register_date(self) -> datetime:
        """Last login date property.

        Lru caching the register date to avoid unnecessary database queries,
        (register_date needs to be collected only once, it is not possible to change it.)

        :returns: the register date of current user

        """
        return self.get_value("register_date")

    @property
    def vault_unlocked(self) -> bool:
        """Return the current state of vault."""
        return self._vault_unlocked

    @vault_unlocked.setter
    def vault_unlocked(self, value: bool) -> None:
        """Unlock the vault and set a new vault unlock date."""
        if value is True:
            self._current_vault_unlock_date = self.get_value("last_vault_unlock_date")
            self.update_date("last_vault_unlock_date")
        self._vault_unlocked = value

    @property
    def current_vault_unlock_date(self) -> datetime:
        """Return the 'previous' date when the vault of the current user has been unlocked."""
        return self._current_vault_unlock_date

    def vault_pages(self, key: Optional[bytes] = None) -> Generator[Vault, None, None]:
        """Yield registered vault pages tied to the current account.

        :param key: Optional argument to decrypt the password with a different key

        """
        with self.database.database_manager() as db:
            # not using f-string due to SQL injection
            sql = """SELECT *
                       FROM lightning_pass.vaults
                      WHERE user_id = {}""".format(
                "%s",
            )
            # expecting a sequence thus val has to be a tuple (created by the trailing comma)
            db.execute(sql, (self.user_id,))
            result = db.fetchall()

        # slice first element -> database primary key
        yield from (
            self.vaults.Vault(
                *vault[1:6],
                self.decrypt_vault_password(
                    vault[6],
                    key if key else self.master_key,
                ),
                *vault[7:],
            )
            for vault in result
            if vault
        )

    @property
    def vault_pages_int(self) -> int:
        """Return an integer with the amount of vault pages a user has registered."""
        return sum(1 for _ in self.vault_pages())

    @property
    def master_key(self) -> bytes:
        """Return the current key derived from the master password."""
        return self.pwd_hashing.pbkdf3hmac_key(
            self._master_key_str,
            self.hashed_vault_credentials.salt,
        )

    @master_key.setter
    def master_key(self, data: PasswordData) -> None:
        """Set a new master key and it's salt.

        :param data: The data container will all the needed information

        :raises AccountDoesNotExist: if the normal password is not correct
        :raises PasswordsDoNotMatch: if the master passwords do not match
        :raises InvalidPassword: if the master password doesn't meet the required pattern

        """
        self.validate_password_data(data)

        data = self.pwd_hashing.hash_master_password(data.new_password)
        self.set_value(data.hash, "master_key")
        self.set_value(data.salt, "master_salt")

    @property
    def hashed_vault_credentials(self) -> bool | HashedVaultCredentials:
        """Return the storage of vault hashing credentials."""
        try:
            return self.pwd_hashing.HashedVaultCredentials(
                self.get_value("master_key").encode("utf-8"),
                self.get_value("master_salt").encode("utf-8"),
            )
        except AttributeError:
            # if there are no results, encoding NoneType will result in the error
            return False

    def encrypt_vault_password(self, password: str | bytes) -> Union[bytes, bool]:
        """Return encrypted password with the current ``vault_key``.

        :param password: The password to encrypt

        """
        if isinstance(password, str):
            password = password.encode("utf-8")
        return self.pwd_hashing.encrypt_vault_password(self.master_key, password)

    def decrypt_vault_password(
        self,
        password: str | bytes,
        key: Optional[bytes] = None,
    ) -> str:
        """Decrypt given vault password and return it.

        :param password: The password to decrypt
        :param key: Optional argument to decrypt the password with a different key

        """
        if isinstance(password, str):
            password = password.encode("utf-8")
        return self.pwd_hashing.decrypt_vault_password(
            key if key else self.master_key,
            password,
        )


if __name__ == "__main__":
    acc = Account(54)

    acc._master_key_str = "Register123+"

    enc = acc.encrypt_vault_password(b"test")
    print(enc)
    print(acc.decrypt_vault_password(enc))
