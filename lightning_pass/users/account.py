"""Module containing the Account class and other functions related to accounts."""
from __future__ import annotations

import functools
from datetime import datetime
from typing import TYPE_CHECKING, Generator, Optional, TypeVar, Union

from PyQt5.QtGui import QPixmap

from lightning_pass.settings import DATABASE_FIELDS
from lightning_pass.users import password_hashing, vaults
from lightning_pass.util import credentials, database
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


class CacheDict(dict):
    def __setitem__(self, key, value):
        if key not in DATABASE_FIELDS:
            raise KeyError(f"Caching of the key {key!r} is not supported.")
        dict.__setitem__(self, key, value)


_V = TypeVar("_V", bound=Validator)


class Account:
    """This class holds information about the currently logged in user."""

    __slots__ = (
        "_user_id",
        "_current_login_date",
        "_vault_unlocked",
        "_current_vault_unlock_date",
        "_master_key_str",
        "_cache",
    )

    credentials = credentials
    database = database
    pwd_hashing = password_hashing
    vaults = vaults

    username: _V = UsernameValidator()
    password: _V = PasswordValidator()
    email: _V = EmailValidator()

    def __init__(self, user_id: int) -> None:
        """Construct the class.

        :param user_id: Database primary key ``id`` of the account

        """
        self._user_id = user_id

        self._cache = CacheDict()

        try:
            self._current_login_date = self.last_login_date
        except AttributeError:
            self._current_login_date = None

        self._vault_unlocked = False

        try:
            self._current_vault_unlock_date = self.last_vault_unlock_date
        except AttributeError:
            self._current_vault_unlock_date = None

        self._master_key_str = r""

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.user_id!r})"

    def __bool__(self) -> bool:
        """Return the boolean value of instances' user id."""
        return bool(self.user_id)

    def __getattr__(self, key) -> Optional[Union[bytes, int, str, datetime]]:
        """Return the key associated with the same in key in database, otherwise raise error.

        :param key: Key of the looked up attribute

        :raises AttributeError: if the key is not in the database

        """
        if key in DATABASE_FIELDS and self:
            try:
                return self._cache[key]
            except KeyError:
                value = self.credentials.get_user_item(self.user_id, "id", key)
                self._cache |= {key: value}
                return value
        else:
            raise AttributeError(
                f"Object {self!r} has no attribute {key!r}.",
            )

    def __setattr__(self, key, value) -> None:
        """Set a new attribute, use database if the key is in database (and _cache the new value).

        :param key: The key of the new attribute
        :param value: The value of the new attribute

        """
        if key in DATABASE_FIELDS:
            credentials.set_user_item(
                user_identifier=self.user_id,
                identifier_column="id",
                result=value,
                result_column=key,
            )
            self._cache |= {key: value}
        else:
            super().__setattr__(key, value)

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

        :returns: ``Account`` object instantiated with current user id

        :raises UsernameAlreadyExists: if username is already registered in the database
        :raises InvalidUsername: if username doesn't match the required pattern
        :raises PasswordDoNotMatch: if password and confirm_password are not the same
        :raises InvalidPassword: if password doesn't match the required pattern
        :raises EmailAlreadyExists: if email is already registered in the database
        :raises InvalidEmail: if email doesn't match the email pattern

        """
        cls.__dict__["username"].validate(username)
        cls.__dict__["password"].validate((password, confirm_password))
        cls.__dict__["email"].validate(email)

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

        :raises AccountDoesNotExist: if the username validation fails

        """
        cls.__dict__["username"].validate(username, should_exist=True)
        cls.__dict__["password"].authenticate(
            password,
            cls.credentials.get_user_item(
                username,
                "username",
                "password",
            ),
        )

        account = cls(cls.credentials.get_user_item(username, "username", "id"))
        account._current_login_date = account.last_login_date
        account.update_date("last_login_date")

        return account

    def set_value(
        self,
        result: Union[int, str, bytes, datetime],
        result_column: str,
    ) -> None:
        """Simplify setting and caching user values.

        :param result: Value which we're inserting
        :param result_column: Column where to insert the value

        """
        credentials.set_user_item(self.user_id, "id", result, result_column)
        self._cache |= {result_column: result}

    def validate_password_data(self, data: PasswordData) -> None:
        """Validate given password data container.

        Used when validating master password or new account password.
        Both of these operations use the same data containers.

        :param data: The data container

        :raises InvalidPassword: If the new password doesn't match the required pattern
            Uses the validator of the current account
        :raises PasswordsDoNotMatch: If the passwords do not match
        :raises AccountDoesNotExist: If the authentication fails

        """
        validator = self.__class__.__dict__["password"]
        validator.validate((data.new_password, data.confirm_new))
        validator.authenticate(data.new_password, self.password)

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

    def reset_password(self, password: str, confirm_password: str) -> None:
        """Reset user's password.

        :raises InvalidPassword: if the pattern check fails
        :raises PasswordsDoNotMatch: if the two passwords do not match

        """
        self.__class__.__dict__["password"].validate((password, confirm_password))

        self.__setattr__("password", self.pwd_hashing.hash_password(password))

    @functools.cache
    def profile_picture_pixmap(self) -> QPixmap:
        """Return the current profile picture ``QPixmap``.

        :returns: The ``QPixmap`` of the profile picture

        """
        return QPixmap(
            str(self.credentials.get_profile_picture_path(self.profile_picture)),
        )

    def current_login_date(self) -> datetime:
        """Return the 'previous' date when the current user has been logged in."""
        return self._current_login_date

    @property
    def vault_unlocked(self) -> bool:
        """Return the current state of vault."""
        return self._vault_unlocked

    @vault_unlocked.setter
    def vault_unlocked(self, value: bool) -> None:
        """Unlock the vault and set a new vault unlock date."""
        if value:
            self._current_vault_unlock_date = self.last_vault_unlock_date
            self.update_date("last_vault_unlock_date")
        self._vault_unlocked = value

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

        if not result:
            return None

        yield from (
            self.vaults.Vault._make(
                (
                    # slice first element -> database primary key
                    *vault[1:6],
                    self.decrypt_vault_password(
                        # need raw string for decryption
                        vault[6].encode("unicode_escape"),
                        key if key else self.master_key,
                    ),
                    *vault[7:],
                ),
            )
            for vault in result
            if vault
        )

    @property
    def master_key(self) -> bool | bytes:
        """Return the current key derived from the master password."""
        try:
            return self.pwd_hashing.pbkdf3hmac_key(
                self._master_key_str.encode("utf-8"),
                self.vault_salt.encode("utf-8"),
            )
        except AttributeError:
            return False

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
        self.set_value(data.hash, "vault_key")
        self.set_value(data.salt, "vault_salt")

    def hashed_vault_credentials(self) -> bool | HashedVaultCredentials:
        """Return the storage of vault hashing credentials."""
        try:
            return self.pwd_hashing.HashedVaultCredentials(
                credentials.get_user_item(self.user_id, "id", "vault_key").encode(
                    "utf-8",
                ),
                self.vault_salt.encode("utf-8"),
            )
        except AttributeError:
            # if there are no results, encoding NoneType will result in the error
            return False

    def encrypt_vault_password(self, password: str | bytes) -> Union[bytes, bool]:
        """Return encrypted password with the current ``master_key``.

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


__all__ = [
    "Account",
]
