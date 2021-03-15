"""Test module for the users package."""
from __future__ import annotations

from typing import Union

import pytest

from lightning_pass.util.util import Password


@pytest.fixture()
def password_cls() -> Password:
    """Return Password object.

    :returns: empty Password class

    """
    return Password(..., ...)


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


__all__ = [
    "password_cls",
    "test_check_password_match",
]
