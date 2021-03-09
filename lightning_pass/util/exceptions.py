class InvalidUsername(AttributeError):
    """Raised when a username doesn't meet a required username pattern."""


class InvalidPassword(AttributeError):
    """Raised when a password doesn't meet a required password pattern."""


class InvalidEmail(AttributeError):
    """Raised when an email doesn't meet a required email pattern."""


class UsernameAlreadyExists(AttributeError):
    """Raised when a username is already registered in a database."""


class EmailAlreadyExists(AttributeError):
    """Raised when an email is already registered in a database."""


class PasswordsDoNotMatch(AttributeError):
    """Raised when 2 password don't match."""


class AccountDoesNotExist(AttributeError):
    """Raised when user tries to login with incorrect login details."""
