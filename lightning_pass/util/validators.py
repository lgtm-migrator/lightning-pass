import re
import secrets
from abc import ABC, abstractmethod
from typing import Optional, Union

import bcrypt
import validator_collection

import lightning_pass.util.credentials as credentials
from lightning_pass.util.exceptions import ValidationFailure


class Validator(ABC):
    @classmethod
    @abstractmethod
    def validate(cls, item):
        cls.pattern(item)

    @staticmethod
    @abstractmethod
    def pattern(item):
        pass


class PublicValidator(Validator):
    @classmethod
    @abstractmethod
    def validate(cls, item):
        cls.pattern(item)
        cls.unique(item)

    @staticmethod
    @abstractmethod
    def unique(item):
        pass


class UsernameValidator(PublicValidator):
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
        if (
            not username
            # length
            or len(username) < 5
            # special char
            or len(username) - len(re.findall(r"[A-Za-z0-9_]", username)) > 0
        ):
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
        if not validator_collection.checkers.is_email(email):
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

        Password pattern:
            1) must be at least 8 characters long
            2) must contain at least 1 capital letter
            3) must contain at least 1 number
            4) must contain at least 1 special character

        :param password: Password to check

        :returns: True or False depending on the pattern check

        """
        if (
            # length
            len(password) < 8
            # capital letters
            or len(re.findall(r"[A-Z]", password)) <= 0
            # numbers
            or len(re.findall(r"[0-9]", password)) <= 0
            # special chars
            or len(password) - len(re.findall(r"[A-Za-z0-9]", password)) <= 0
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
