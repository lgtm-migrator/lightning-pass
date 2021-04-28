from __future__ import annotations

import pytest

from lightning_pass.util.exceptions import (
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
)
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
    "username",
    [
        "User",
        "       ",
        "1111",
        "special*",
        " username ",
        "\a\a\a\a\\" "",
    ],
)
def test_username_pattern(username_validator, username):
    with pytest.raises(InvalidUsername):
        username_validator.pattern(username)


@pytest.mark.parametrize(
    "email",
    [
        "email@company..com",
        "@company.com",
        "email.com",
        "email@company",
        "@",
        "  ",
        "@email@email.com",
        "email@email.c",
        "email @ company.com",
    ],
)
def test_email_pattern(email_validator, email):
    with pytest.raises(InvalidEmail):
        email_validator.pattern(email)


@pytest.mark.parametrize(
    "password",
    [
        "Pass123456",
        "******aa7",
        "2Short<",
        "no_upper1+",
        "*UPPPER_ONLY1",
        "",
        "Whitespaces12*    ",
        "  Password123+   ",
    ],
)
def test_password_pattern(password_validator, password):
    with pytest.raises(InvalidPassword):
        password_validator.pattern(password)
