from __future__ import annotations

import pytest

from lightning_pass.util.validators import (
    EmailValidator,
    PasswordValidator,
    UsernameValidator,
)


@pytest.fixture
def username_validator() -> UsernameValidator:
    """Return username validator instance."""
    return UsernameValidator()


@pytest.fixture
def password_validator() -> PasswordValidator:
    """Return password validator instance."""
    return PasswordValidator()


@pytest.fixture
def email_validator() -> EmailValidator:
    """Return email validator instance."""
    return EmailValidator()


@pytest.mark.parametrize(
    "username, result",
    [
        ("Username", True),
        ("number1", True),
        ("11111", True),
        ("special*", False),
        ("", False),
    ],
)
def test_username_pattern(username_validator, username, result):
    assert username_validator.pattern(username) is result


@pytest.mark.parametrize(
    "email, result",
    [
        ("email@company.com", True),
        ("@company.com", False),
        ("email.com", False),
        ("email@company", False),
        ("", False),
    ],
)
def test_email_pattern(email_validator, email, result):
    assert email_validator.pattern(email) is result


@pytest.mark.parametrize(
    "password, result",
    [
        ("Pass123+", True),
        ("******Aa7", True),
        ("2Short<", False),
        ("no_upper1+", False),
        ("*UPPPER_ONLY1", False),
        ("", False),
        ("Whitespaces12*    ", False),
        ("  Password123+   ", False),
    ],
)
def test_password_pattern(password_validator, password, result):
    assert password_validator.pattern(password) is result


def test_password_unique(password_validator):
    assert password_validator.unique("") is False
