"""Module containing all custom exceptions used throughout the project."""


class AccountException(Exception):
    """Base exception for all exceptions connected to account management."""


class ValidationFailure(AccountException, ValueError):
    """Base exception for all exceptions connected to validation failures."""


class InvalidUsername(ValidationFailure):
    """Raised when a username doesn't meet a required username pattern."""


class InvalidPassword(ValidationFailure):
    """Raised when a password doesn't meet a required password pattern."""


class InvalidEmail(ValidationFailure):
    """Raised when an email doesn't meet a required email pattern."""


class InvalidResetToken(ValidationFailure):
    """Raised when a token is invalid."""


class UsernameAlreadyExists(ValidationFailure):
    """Raised when a username is already registered in a database."""


class EmailAlreadyExists(ValidationFailure):
    """Raised when an email is already registered in a database."""


class PasswordsDoNotMatch(ValidationFailure):
    """Raised when 2 password don't match."""


class AccountDoesNotExist(AccountException):
    """Raised when user tries to login with incorrect login details."""


class VaultException(AccountException):
    """Base exception for all exceptions connected to vault management."""


class InvalidURL(ValidationFailure):
    """Raised when an url doesn't match the url pattern."""


__all__ = [
    "AccountDoesNotExist",
    "AccountException",
    "EmailAlreadyExists",
    "InvalidEmail",
    "InvalidPassword",
    "InvalidResetToken",
    "InvalidURL",
    "InvalidUsername",
    "PasswordsDoNotMatch",
    "UsernameAlreadyExists",
    "ValidationFailure",
    "VaultException",
]
