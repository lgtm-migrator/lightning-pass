import re
import secrets
from abc import ABC, abstractmethod
from typing import Optional, Union

import bcrypt
from validator_collection import checkers

import lightning_pass.util.credentials as credentials
from lightning_pass.util.exceptions import ValidationFailure


class Validator(ABC):
    """Base class for validation of account data."""

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}()"

    @classmethod
    @abstractmethod
    def validate(cls, item: Union[str, bytes]) -> None:
        """Perform every validation of the child class.

        :param item: The item to validate

        :raises ValidationFailure: if the validation fails

        """

    @staticmethod
    @abstractmethod
    def pattern(item: Union[str, bytes]) -> bool:
        """Validate pattern for the given item.

        :param item: The item to validate

        """


class UsernameValidator(Validator):
    """Validator for username."""

    @classmethod
    def validate(cls, username: str) -> None:
        """Perform all validation checks for the given username.

        :param username: The username to be validated.

        :raises ValidationFailure: if the validation fails

        """
        if not cls.pattern(username) or not cls.unique(username):
            raise ValidationFailure

    @staticmethod
    def pattern(username: str) -> bool:
        """Check whether a given username matches a required pattern.

        Username pattern:
            1) 5 characters
            2) No special characters

        :param str username: Username to check

        :returns: True if the validation is passed, False otherwise

        """
        if not re.match(r"^[\w]{5,}$", username):
            return False
        return True

    @staticmethod
    def unique(username: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database.

        :param username: Username to check
        :param should_exist: Influences the checking approach, defaults to False

        :returns: True if the validation if passed, False otherwise

        :raises ValidationFailure: if validation fails

        """
        if not credentials.check_item_existence(
            username,
            "username",
            should_exist=should_exist,
        ):
            return False
        return True


class EmailValidator(Validator):
    """Validator for email addresses."""

    @classmethod
    def validate(cls, email: str):
        """Perform all validation checks for the given email.

        :param email: The email to be validated

        :raises ValidationFailure: if any validation fails

        """
        if not cls.pattern(email) or not cls.unique(email):
            raise ValidationFailure

    @staticmethod
    def pattern(email: str) -> bool:
        """Check whether a given email passes the email check.

        :param email: Email to check

        :returns: True if the pattern validation is passed, False otherwise

        """
        return checkers.is_email(email)

    @staticmethod
    def unique(email: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param email: Email to check
        :param should_exist: Influences the checking approach, defaults to False

        :returns: True if the validation is passed, False otherwise

        """
        if not credentials.check_item_existence(
            email,
            "email",
            should_exist=should_exist,
        ):
            return False
        return True


class PasswordValidator(Validator):
    """Validator for password."""

    @classmethod
    def validate(cls, email: str):
        """Perform all validation checks.

        :param email: The password to validate

        :raises ValidationFailure: if the validation fails

        """
        if not cls.pattern(email):
            raise ValidationFailure

    @staticmethod
    def pattern(password: str) -> bool:
        """Check whether password matches a required pattern.

        Password must contain at least:
            1) 8 characters
            2) 1 lowercase character
            2) 1 uppercase character
            3) 1 digit
            4) 1 special character

        :param password: Password to check

        :returns: True if the validation is passed, False otherwise

        """
        if not re.match(
            #    digits   lowercase  uppercase  special   length
            r"^(?=.+[\d])(?=.+[a-z])(?=.+[A-Z])(?=.+[^\w]).{8,}$",
            password,
        ):
            return False
        return True

    @staticmethod
    def match(first: Union[str, bytes], second: Union[str, bytes]) -> bool:
        """Check whether the first and second parameters match.

        :param first: The first parameter
        :param second: The second parameter

        :returns: True if the first and second parameters match, False otherwise

        """
        if not secrets.compare_digest(str(first), str(second)):
            return False
        return True

    @staticmethod
    def authenticate(
        password: Union[str, bytes],
        stored: Union[str, bytes],
    ) -> bool:
        """Check whether the first parameter is the same as the second hashed parameter.

        :param password: The password in a string format
        :param stored: The password hash

        :returns: True if the the first and second parameters match, False otherwise

        """
        if not bcrypt.checkpw(
            password.encode("utf-8"),
            stored.encode("utf-8"),
        ):
            return False
        return True


__all__ = [
    "EmailValidator",
    "PasswordValidator",
    "UsernameValidator",
    "Validator",
]
