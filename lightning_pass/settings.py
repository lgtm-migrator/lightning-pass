"""Module with project constants and DDLs for database."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import dotenv
import qdarkstyle

from lightning_pass.util import database


def parent_folder() -> Path:
    """Return a ``Path`` to the parent folder of the settings script."""
    return Path(__file__).parent


def static_folder() -> Path:
    """Return a ``Path`` to the static folder located in the gui folder."""
    return parent_folder() / "gui/static"


TRAY_ICON = static_folder() / "favicon.ico"
PFP_FOLDER = parent_folder() / "users/profile_pictures"
LOG = parent_folder().parent / "misc/logs.log"


def light_stylesheet() -> str:
    """Return the stylesheet to be associated with light mode."""
    return ""


def dark_stylesheet() -> str:
    """Return the stylesheet to be associated with dark mode."""
    return qdarkstyle.load_stylesheet(qt_api="PyQt5")


dotenv.load_dotenv()


@dataclass(frozen=True)
class Credentials:
    """Store the credentials to be used while using a database and an email account."""

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASS")
    db_database = os.getenv("DB_DB")

    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASS")


def _copy(self: Path, target: Path) -> None:
    """Copy a given file to the given target destination.

    :param Path self: What to copy
    :param Path target: Where to copy self

    """
    assert self.is_file()
    shutil.copy(self, target)


# monkey patch copy functionality into every Path object
# noinspection PyTypeHints
Path.copy = _copy  # type: ignore


_CREDENTIALS_DDL = """CREATE TABLE IF NOT EXISTS `credentials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` char(60) NOT NULL,
  `email` varchar(255) NOT NULL,
  `profile_picture` varchar(255) NOT NULL DEFAULT 'default.png',
  `last_login_date` timestamp NULL DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `master_password` varchar(255) DEFAULT NULL,
  `last_vault_unlock_date` timestamp NULL DEFAULT NULL,
  `vault_key` char(60) DEFAULT NULL,
  `vault_salt` char(29) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

_TOKENS_DDL = """CREATE TABLE IF NOT EXISTS `tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `token_UNIQUE` (`token`),
  KEY `id_idx` (`user_id`),
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `credentials` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

_VAULTS_DDL = """CREATE TABLE IF NOT EXISTS `vaults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `platform_name` varchar(255) NOT NULL,
  `website` varchar(512) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` char(100) NOT NULL,
  `vault_index` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `id_idx` (`user_id`),
  CONSTRAINT `id` FOREIGN KEY (`user_id`) REFERENCES `credentials` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

DATABASE_FIELDS = {
    "id",
    "username",
    "password",
    "email",
    "profile_picture",
    "last_login_date",
    "register_date",
    "last_vault_unlock_date",
    "master_password",
    "vault_key",
    "vault_salt",
}


def setup_database() -> None:
    """Setup the three databases."""
    with database.database_manager() as db:
        db.execute(_CREDENTIALS_DDL)
        db.execute(_TOKENS_DDL)
        db.execute(_VAULTS_DDL)
