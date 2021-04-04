"""Module containing the Vault class."""
from __future__ import annotations

from typing import NamedTuple, Union

import lightning_pass.util.credentials as credentials
import lightning_pass.util.database as database
from lightning_pass.util.exceptions import InvalidURL, InvalidEmail, VaultException


class Vault(NamedTuple):
    user_id: int
    platform_name: str
    website: str
    username: str
    email: str
    password: Union[str, bytes]
    vault_index: int


def update_vault(vault: Vault) -> None:
    if not credentials.validate_url(vault.website):
        raise InvalidURL

    if not credentials.Email.check_email_pattern(vault.email):
        raise InvalidEmail

    if (
        not vault.user_id
        or not vault.platform_name
        or not vault.website
        or not vault.username
        or not vault.email
        or not vault.password
    ):
        raise VaultException

    if credentials.check_item_existence(
        str(vault.user_id),
        "user_id",
        "vaults",
        should_exist=True,
        second_key=vault.vault_index,
        second_key_column="vault_index",
    ):
        _update_vault(vault)
    else:
        _new_vault(vault)


def delete_vault(vault: Vault) -> None:
    """"""


def _update_vault(vault: Vault) -> None:
    """Update an already existing vault

    :param vault: The ``Vault`` object containing all of the updated vault data

    """
    with database.database_manager() as db:
        sql = """UPDATE lightning_pass.vaults SET
        platform_name = %s,
        website = %s,
        username = %s,
        email = %s,
        password = %s
        WHERE user_id = %s
        AND vault_index = %s
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
                vault.platform_name,
                vault.email,
                vault.username,
                vault.email,
                credentials.Password.hash_password(vault.password),
                vault.user_id,
                vault.vault_index,
            ),
        )


def _new_vault(vault: Vault) -> None:
    """Insert a new page into the database

    :param vault: The ``Vault`` object containing all of the vault data

    :raises InvalidURL: if the submitted URL is not an URL
    :raises InvalidEmail: if the submitted email is not an email
    :raises VaultException: if some vault page data is missing

    """
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
                vault.user_id,
                vault.platform_name,
                vault.website,
                vault.username,
                vault.email,
                credentials.Password.hash_password(vault.password),
                vault.vault_index,
            ),
        )


__all__ = ["Vault"]
