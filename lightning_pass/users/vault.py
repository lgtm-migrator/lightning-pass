"""Vault."""


class Vault:
    def __init__(
        self, user_id, platform_name, website, username, email, password, vault_index
    ):
        self.user_id = user_id
        self.platform_name = platform_name
        self.website = website
        self.username = username
        self.email = email
        self.password = password
        self.vault_index = vault_index
