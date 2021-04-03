"""Module containing the Vault class."""
from __future__ import annotations

import copy
from typing import Optional, NamedTuple

import lightning_pass.util.credentials as credentials
import lightning_pass.util.database as database
from lightning_pass.util.exceptions import InvalidURL, InvalidEmail, VaultException


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
    """Insert a new page into the database

    :param user_id: Tie the new vault to the user with the given id
    :param platform_name: The name of the platform, eg. StackOverflow, Gitlab,...
    :param website: The website link to the chosen platform
    :param username: The username used to sign into the platform
    :param email: The email used to sign in into the platform
    :param password: The password used to sign in into the platform
    :param vault_index: Indicates which vault page is being created/edited

    :returns: ``Vault`` instantiated with the mew values, if everything goes correctly

    :raises InvalidURL: if the submitted URL is not an URL
    :raises InvalidEmail: if the submitted email is not an email
    :raises VaultException: if some vault page data is missing

    """
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
    with database.database_manager() as db:
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
