import re
import secrets
from abc import ABC, abstractmethod
from typing import Optional, Union

import bcrypt
from validator_collection import checkers

import lightning_pass.util.credentials as credentials
from lightning_pass.util.exceptions import ValidationFailure


class Validator(ABC):
    def __init__(self, item) -> None:
        self.item = item

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.item})"

    def __str__(self) -> str:
        return self.item

    @classmethod
    @abstractmethod
    def validate(cls, item):
        cls.pattern(item)

    @staticmethod
    @abstractmethod
    def pattern(item):
        pass


class UsernameValidator(Validator):
    @classmethod
    def validate(cls, username: str):
        cls.pattern(username)
        cls.unique(username)

    @staticmethod
    def pattern(username: str) -> bool:
        """Check whether a given username matches a required pattern.

        Username pattern:
            1) must be at least 5 characters long
            2) mustn't contain special characters

        :param str username: Username to check

        :returns: True or False depending on the result

        """
        if not re.match(r"^\w{5,}$", username):
            raise ValidationFailure
        return True

    @staticmethod
    def unique(username: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database.

        :param username: Username to check
        :param should_exist: Influences the checking approach, defaults to False

        :returns: True or False depending on the result

        """
        if not credentials.check_item_existence(
            username,
            "username",
            should_exist=should_exist,
        ):
            raise ValidationFailure
        return True


class EmailValidator(Validator):
    @classmethod
    def validate(cls, email: str):
        cls.pattern(email)
        cls.unique(email)

    @staticmethod
    def pattern(email: str) -> bool:
        """Check whether a given email passes the email check.

        :param email: Username to check

        :returns: True or False depending on the result

        """
        if not checkers.is_email(email):
            raise ValidationFailure
        return True

    @staticmethod
    def unique(email: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param email: Email to check
        :param should_exist: Influences the checking approach, defaults to False

        :returns: True or False depending on the result

        """
        if not credentials.check_item_existence(
            email,
            "email",
            should_exist=should_exist,
        ):
            raise ValidationFailure
        return True


class PasswordValidator(Validator):
    @classmethod
    def validate(cls, password):
        cls.pattern(password)

    @staticmethod
    def pattern(password: str):
        """Check whether password matches a required pattern.

        Password must contain at least:
            1) 8 characters
            2) 1 lowercase letter
            2) 1 uppercase letter
            3) 1 number
            4) 1 special character

        :param password: Password to check

        :returns: True or False depending on the pattern check

        """
        if not re.match(
            #   numbers   lowercase  uppercase  special   length
            r"^(?=.+[\d])(?=.+[a-z])(?=.+[A-Z])(?=.+[^\w]).{8,}$",
            password,
        ):
            raise ValidationFailure
        return True

    @staticmethod
    def match(first: Union[str, bytes], second: Union[str, bytes]) -> bool:
        if not secrets.compare_digest(str(first), str(second)):
            raise ValidationFailure
        return True

    @staticmethod
    def authenticate(
        password: Union[str, bytes],
        stored: Union[str, bytes],
    ) -> bool:
        if not bcrypt.checkpw(
            password.encode("utf-8"),
            stored.encode("utf-8"),
        ):
            raise ValidationFailure
        return True


__all__ = [
    "EmailValidator",
    "PasswordValidator",
    "UsernameValidator",
    "Validator",
]
