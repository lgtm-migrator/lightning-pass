"""Module containing everything connected to password hashing for secure storage in database."""
import base64
from typing import NamedTuple, Union

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def hash_password(password: Union[str, bytes]) -> bytes:
    """Hash and return password with bcrypt.

    :param str password: Password to hash

    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt())


class HashedVaultCredentials(NamedTuple):
    """Store the credentials."""

    hash: bytes
    salt: bytes


def pbkdf3hmac_key(password: Union[str, bytes], salt: bytes):
    """Derive and return a new key from the given password.

    :param password: The password which will be tied to the key
    :param salt: Make it possible to derive the same key again

    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def hash_master_password(password: str) -> HashedVaultCredentials:
    """Return hashed master password key with the used salt.

    :param password: The password to be used while hashing

    """
    salt = bcrypt.gensalt()
    key = pbkdf3hmac_key(password, salt)
    return HashedVaultCredentials(bcrypt.hashpw(key, bcrypt.gensalt()), salt)


def auth_derived_key(password: str, stored: HashedVaultCredentials) -> bool:
    """Authenticate whether the given password matches the stored set of values.

    :param password: The password to evaluate
    :param stored: The stored data

    """
    key = pbkdf3hmac_key(password, stored.salt)
    return bcrypt.checkpw(key, stored.hash)


def encrypt_vault_password(key: bytes, password: Union[str, bytes]) -> bytes:
    """Encrypt and return the given vault password.

    :param key: The key to be used during the encryption
    :param password: The password to encrypt

    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    f = Fernet(key)
    return f.encrypt(password)


def decrypt_vault_password(key: bytes, password: Union[str, bytes]) -> Union[str, bool]:
    """Decrypt and return the given vault password.

    :param key: The key to be used during the decryption
    :param password: The password to decrypt

    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    f = Fernet(key)
    try:
        return f.decrypt(password).decode()
    except InvalidToken:
        return False


__all__ = [
    "HashedVaultCredentials",
    "auth_derived_key",
    "decrypt_vault_password",
    "encrypt_vault_password",
    "hash_master_password",
    "hash_password",
    "pbkdf3hmac_key",
]
