from __future__ import annotations

import functools
import re
import secrets
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Pattern, Union

import bcrypt
from validator_collection import checkers

from lightning_pass.util import credentials, regex
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

if TYPE_CHECKING:
    from lightning_pass.users.account import Account


def partial_class(cls, *args, **kwargs):
    """Create a partial class like a partial function with ``functools.partial``.

    :returns: The partial class

    """

    class Partial(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwargs)

        def __repr__(self):
            return f"Partial class of {cls.__qualname__!r} in {cls.__module__!r}"

    return Partial


class Validator(ABC):
    """Base validator class."""

    __slots__ = "private_name", "public_name"

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}()"

    def __set_name__(self, owner, name):
        """Set the field names."""
        self.private_name = f"_{name}"
        self.public_name = name

    def __get__(self, instance: Account, owner):
        """Return the currently stored value."""
        return instance.__getattr__(self.public_name)

    def __set__(self, instance: Account, value):
        """Validate and set the new value."""
        self.validate(value)
        setattr(instance, self.public_name, value)

    @abstractmethod
    def validate(self, value: Any, should_exist: bool = False) -> None:
        """Perform every validation of the child class.

        :param value: The item to validate
        :param should_exist: To be passed into the unique check

        :raises Type[ValidationFailure]: if the validation fails

        """
        self.pattern(value)
        self.unique(value, should_exist=should_exist)

    @abstractmethod
    def pattern(self, value: Union[str, bytes]) -> None:
        """Validate pattern for the given item.

        :param value: The item to validate

        """
        if not re.fullmatch(r"", value):
            raise ValidationFailure

    @abstractmethod
    def unique(self, value: Union[str, bytes], should_exist: bool = False) -> None:
        """Validate that the given item does not already exist.

        :param value: The item to validate
        :param should_exist: Whether the item should already be present in the database or not

        """
        if not credentials.check_item_existence(
            value,
            self.public_name,
            should_exist=should_exist,
        ):
            raise ValidationFailure


class Username(Validator):
    """Validator for username."""

    __slots__ = "re_pattern"

    def __init__(self, re_pattern: Pattern):
        self.re_pattern = re_pattern

    def validate(self, username: str, should_exist: bool = False) -> None:
        """Perform all validation checks for the given username.

        :param username: The username to be validated.
        :param should_exist: To be passed into the unique check

        :raises Type[ValidationFailure]: if the validation fails

        """
        self.pattern(username)
        self.unique(username, should_exist=should_exist)

    def pattern(self, username: str) -> None:
        """Check whether a given username matches the pattern used to instantiate this class.

        :param username: The username to check

        :raises InvalidUsername: if the username doesn't match the pattern

        """
        if not re.fullmatch(self.re_pattern, username):
            raise InvalidUsername

    def unique(self, username: str, should_exist: bool = False) -> None:
        """Check whether a username already exists in a database.

        :param username: Username to check
        :param should_exist: Influences the checking approach, defaults to False

        :raises UsernameAlreadyExists: if the username already already exists

        """
        if not credentials.check_item_existence(
            username,
            self.public_name,
            should_exist=should_exist,
        ):
            raise UsernameAlreadyExists


class Email(Validator):
    """Validator for email addresses."""

    __slots__ = ()

    def validate(self, email: str, should_exist: bool = False) -> None:
        """Perform all validation checks for the given email.

        :param email: The email to be validated
        :param should_exist: To be passed into the unique check

        :raises Type[ValidationFailure]: if the validation fails

        """
        self.pattern(email)
        self.unique(email, should_exist=should_exist)

    def pattern(self, email: str) -> None:
        """Check the pattern of the given email.

        :param email: The email to check

        :raises InvalidEmail: if the email doesn't pass the email verification

        """
        if not checkers.is_email(email):
            raise InvalidEmail

    def unique(self, email: str, should_exist: bool = False) -> None:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param email: The email to check
        :param should_exist: Influences the checking approach, defaults to False

        :raises EmailAlreadyExists: if the email is already registered in the database

        """
        if not credentials.check_item_existence(
            email,
            self.public_name,
            should_exist=should_exist,
        ):
            raise EmailAlreadyExists


class Password(Validator):
    """Validator for password."""

    __slots__ = "re_pattern"

    def __init__(self, re_pattern: Pattern):
        self.re_pattern = re_pattern

    def __set__(self, instance: Account, data: tuple[str, str]):
        """Override the __set__ method so that it hashes the password."""
        self.validate(data)
        setattr(instance, self.public_name, instance.pwd_hashing.hash_password(data[0]))

    def validate(self, password_data: tuple[str, str], should_exist: bool = False):
        """Perform all validation checks.

        :param password_data: The password to validate
        :param should_exist: To be passed into the unique check

        :raises Type[ValidationFailure]: if the validation fails

        """
        self.pattern(password_data[0])
        self.unique(password_data[0], should_exist=should_exist)
        self.match(password_data[0], password_data[1])

    def pattern(self, password: Union[str, bytes]) -> None:
        """Check whether password matches the pattern used when instantiating this class.

        :param password: The password to check

        :raises InvalidPassword: if the password does not match the pattern

        """
        if not re.fullmatch(self.re_pattern, password):
            raise InvalidPassword

    def unique(self, password: str, should_exist: bool = False) -> bool:
        """Pass since unique validation for passwords is not possible."""

    @staticmethod
    def match(first: Union[str, bytes], second: Union[str, bytes]) -> None:
        """Check whether the first and second parameters match.

        :param first: The first parameter
        :param second: The second parameter

        :raise PasswordsDoNotMatch: if the parameters do not match

        """
        if not secrets.compare_digest(str(first), str(second)):
            raise PasswordsDoNotMatch

    @staticmethod
    def authenticate(
        password: Union[str, bytes],
        stored: Union[str, bytes],
    ) -> None:
        """Check whether the first parameter is the same as the second hashed parameter.

        :param password: The password in a human readable format
        :param stored: The password hash

        :raises AccountDoesNotExist: if the authentication fails

        """
        if not bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8")):
            raise AccountDoesNotExist


UsernameValidator = partial_class(
    Username,
    regex.USERNAME,
)
PasswordValidator = partial_class(
    Password,
    regex.PASSWORD,
)
EmailValidator = partial_class(
    Email,
)


__all__ = [
    "EmailValidator",
    "PasswordValidator",
    "UsernameValidator",
    "Validator",
]
