"""Vault."""
from .account import Account
from lightning_pass.util.database import database_manager


class Vault(Account):
    def __init__(self, user_id, vault_index):
        super().__init__(user_id)
        self.user_id = user_id
        self.vault_index = vault_index

    @staticmethod
    def validate_url(url):
        import validators

        return validators.url(url)

    @classmethod
    def new_vault(
        cls,
        user_id: int,
        platform_name: str,
        website: str,
        username: str,
        email: str,
        password: str,
    ):
        print(cls.validate_url(website))

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
                 VALUES (%d, %s, %s, %s, %s, %s, %s)
            """
            val = (user_id, platform_name, website, username, email, password, ...)

            db.execute(sql, val)

        return cls(user_id, vault_index=...)
