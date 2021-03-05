class Exceptions:
    class InvalidUsername(Exception):
        """Raised when a username doesn't meet a required username pattern."""

    class InvalidPassword(Exception):
        """Raised when a password doesn't meet a required password pattern."""

    class InvalidEmail(Exception):
        """Raised when an email doesn't meet a required email pattern."""

    class UsernameAlreadyExists(Exception):
        """Raised when a username is already registered in a database."""

    class EmailAlreadyExists(Exception):
        """Raised when an email is already registered in a database."""

    class PasswordsDoNotMatch(Exception):
        """Raised when 2 password don't match."""

    class AccountDoesNotExist(Exception):
        """Raised when user tries to login with incorrect login details."""
