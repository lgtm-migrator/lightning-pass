import base64
from typing import NamedTuple, Union

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def hash_password(password: Union[str, bytes]) -> bytes:
    """Hash password with bcrypt.

    :param str password: Password to hash

    :returns: the password hash

    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt())


class HashedVaultCredentials(NamedTuple):
    hash: bytes
    salt: bytes


def pbkdf3hmac_key(password: Union[str, bytes], salt: bytes):
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
    salt = bcrypt.gensalt()
    key = pbkdf3hmac_key(password, salt)
    return HashedVaultCredentials(bcrypt.hashpw(key, bcrypt.gensalt()), salt)


def auth_derived_key(password: str, stored: HashedVaultCredentials) -> bool:
    key = pbkdf3hmac_key(password, stored.salt)
    return bcrypt.checkpw(key, stored.hash)


def encrypt_vault_password(key: bytes, password: Union[str, bytes]) -> bytes:
    if isinstance(password, str):
        password = password.encode("utf-8")
    f = Fernet(key)
    return f.encrypt(password)


def decrypt_vault_password(key: bytes, password: bytes) -> Union[str, bool]:
    f = Fernet(key)
    try:
        return f.decrypt(password).decode()
    except InvalidToken:
        return False


master_password = "master_password"
data = hash_master_password(master_password)
print(auth_derived_key("master", data))
print(auth_derived_key("master_password", data))
encrypted = encrypt_vault_password(pbkdf3hmac_key("aa", data.salt), "i am stored")
print(encrypted)
decrypted = decrypt_vault_password(
    pbkdf3hmac_key(master_password, data.salt),
    encrypted,
)
print(decrypted)
