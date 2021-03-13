"""Module containing all custom exceptions used throughout the project."""


class AccountException(Exception):
    """Base exception for all errors connected to account management."""


class InvalidUsername(AccountException):
    """Raised when a username doesn't meet a required username pattern."""


class InvalidPassword(AccountException):
    """Raised when a password doesn't meet a required password pattern."""


class InvalidEmail(AccountException):
    """Raised when an email doesn't meet a required email pattern."""


class UsernameAlreadyExists(AccountException):
    """Raised when a username is already registered in a database."""


class EmailAlreadyExists(AccountException):
    """Raised when an email is already registered in a database."""


class PasswordsDoNotMatch(AccountException):
    """Raised when 2 password don't match."""


class AccountDoesNotExist(AccountException):
    """Raised when user tries to login with incorrect login details."""


class StopCollectingPositions(AccountException):
    """Raised when all needed mouse positions are collected."""
