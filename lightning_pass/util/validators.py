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
        cls.validate_pattern(item)

    @staticmethod
    @abstractmethod
    def validate_pattern(item):
        pass


class PublicValidator(Validator):
    @classmethod
    @abstractmethod
    def validate(cls, item):
        cls.validate_pattern(item)
        cls.validate_unique(item)

    @staticmethod
    @abstractmethod
    def validate_unique(item):
        pass


class UsernameValidator(PublicValidator):
    @classmethod
    def validate(cls, username: str):
        cls.validate_pattern(username)
        cls.validate_unique(username)

    @staticmethod
    def validate_pattern(username: str) -> bool:
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
    def validate_unique(username: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check
        :param bool should_exist: Influences the checking approach, defaults to False

        :returns: True or False depending on the result

        """
        if not credentials.check_item_existence(
            username, "username", should_exist=should_exist
        ):
            raise ValidationFailure
        return True


class EmailValidator(Validator):
    @classmethod
    def validate(cls, email: str):
        cls.validate_pattern(email)
        cls.validate_unique(email)

    @staticmethod
    def validate_pattern(email: str) -> bool:
        """Check whether a given username matches a required pattern.

        Username pattern:
            1) must be at least 5 characters long
            2) mustn't contain special characters

        :param str username: Username to check

        :returns: True or False depending on the result

        """
        if not validator_collection.checkers.is_email(email):
            raise ValidationFailure
        return True

    @staticmethod
    def validate_unique(email: str, should_exist: Optional[bool] = False) -> bool:
        """Check whether a username already exists in a database and if it matches a required pattern.

        :param str username: Username to check
        :param bool should_exist: Influences the checking approach, defaults to False

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
        cls.validate_pattern(password)

    @staticmethod
    def validate_pattern(password: str):
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
    def validate_match(first: Union[str, bytes], second: Union[str, bytes]) -> bool:
        if not secrets.compare_digest(str(first), str(second)):
            raise ValidationFailure
        return True

    @staticmethod
    def validate_authentication(
        password: Union[str, bytes],
        stored: Union[str, bytes],
    ) -> bool:
        if not bcrypt.checkpw(
            password.encode("utf-8"),
            stored.encode("utf-8"),
        ):
            raise ValidationFailure
        return True
