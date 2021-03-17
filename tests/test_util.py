"""Test module for the users package."""
from __future__ import annotations

from typing import Union

import pytest

from lightning_pass.util.credentials import Username, Password, Email


@pytest.fixture()
def username_cls() -> Username:
    """Return Username object.

    :returns: empty Username class

    """
    return Username(...)


@pytest.fixture()
def password_cls() -> Password:
    """Return Password object.

    :returns: empty Password class

    """
    return Password(..., ...)


@pytest.fixture()
def email_cls() -> Email:
    """Return Username object.

    :returns: empty Email class

    """
    return Email(...)


@pytest.mark.parametrize(
    "username",
    [
        "",
        " ",
        "0",
        "aaaa",
    ],
)
def test_check_username_pattern(username):
    assert not Username.check_username_pattern(username)  # act


@pytest.mark.parametrize(
    "password",
    [
        "",
        " ",
        "1",
        "password",
        "Password",
        "123456789",
        "++++++++",
        "Password1",
        "password+",
    ],
)
def test_check_password_pattern(password):
    assert not Password.check_password_pattern(password)  # act


@pytest.mark.parametrize(
    "password, confirm_password",
    [
        ("str", "str"),
        (r"str", "str"),
        ("str", r"str"),
        (r"str", r"str"),
    ],
)
def test_check_password_match(
    password_cls: Password,
    password: Union[str, bytes],
    confirm_password: Union[str, bytes],
) -> None:
    """Test check_password_match func of Password.

    :param Password password_cls: Password object
    :param Union[str, bytes] password: First password
    :param Union[str, bytes] confirm_password:  Second password

    Fails if func raises an exception.

    """
    password_cls.check_password_match(password, confirm_password)  # act


@pytest.mark.parametrize(
    "password",
    ["PASSWORD12!", "123456P*"],
)
def test_hash_password(password):
    # act
    assert not password == Password.hash_password(password)
    assert not password == password.encode("utf-8")
    assert not password == Password.hash_password(password).decode("utf-8")
    assert len(Password.hash_password(password)) > len(password)
    assert type(Password.hash_password(password)) == bytes


@pytest.mark.parametrize(
    "password, current_password",
    [
        ("PASSWORD1/", "PASSWORD1/"),
    ],
)
def test_authenticate_password(password, current_password):
    with pytest.raises(ValueError):
        Password.authenticate_password(password, current_password)  # act


@pytest.mark.parametrize(
    "email",
    ["", " ", "@", "email@email.1", "email.email@email.email.com", "@email.com"],
)
def test_email_pattern_check(email):
    assert not Email.check_email_pattern(email)  # act


__all__ = [
    "password_cls",
    "test_check_password_match",
]
