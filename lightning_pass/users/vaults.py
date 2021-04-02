"""Module containing the Vault class."""
from __future__ import annotations

import copy
from typing import Optional, NamedTuple

from lightning_pass.util.exceptions import InvalidURL, InvalidEmail, VaultException
from lightning_pass.util.database import database_manager
from lightning_pass.util import credentials


class Vault(NamedTuple):
    user_id: int
    platform_name: str
    website: str
    username: str
    email: str
    password: bytes
    vault_index: int


def new_vault(
    user_id: int,
    platform_name: str,
    website: str,
    username: str,
    email: str,
    password: str,
    vault_index: int,
) -> Optional[Vault]:
    # copy locals object to store given arguments
    args = copy.copy(locals())

    if not credentials.validate_url(website):
        raise InvalidURL

    if not credentials.Email.check_email_pattern(email):
        raise InvalidEmail

    if (
        not user_id
        or not platform_name
        or not website
        or not username
        or not email
        or not password
    ):
        raise VaultException

    # no exceptions raised -> insert into db
    with database_manager() as db:
        sql = """
        INSERT INTO lightning_pass.vaults (        
        user_id,
        platform_name,
        website,
        username,
        email,
        password,
        vault_index
        )
             VALUES (%s, %s, %s, %s, %s, %s, %s)
        """ % (
            "%s",
            "%s",
            "%s",
            "%s",
            "%s",
            "%s",
            "%s",
        )
        db.execute(
            sql,
            (
                user_id,
                platform_name,
                website,
                username,
                email,
                credentials.Password.hash_password(password),
                vault_index,
            ),
        )

    return Vault(*args.values())


__all__ = ["Vault"]
