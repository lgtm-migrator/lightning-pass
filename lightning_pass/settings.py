"""Module with project constants and settings."""
from __future__ import annotations

import os
from pathlib import Path

import dotenv

from .util import database


def parent_folder() -> Path:
    """Return a Path to the parent folder of the settings script."""
    return Path(__file__).parent


def static_folder() -> Path:
    """Return a Path to the static folder located in the gui folder."""
    return parent_folder() / "gui/static"


dotenv.load_dotenv()
DB_DICT = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_DB"),
}
EMAIL_DICT: dict = {
    "email": os.getenv("EMAIL_USER"),
    "password": os.getenv("EMAIL_PASS"),
}

LIGHT_STYLESHEET = static_folder() / "light.qss"
DARK_STYLESHEET = static_folder() / "dark.qss"

TRAY_ICON = static_folder() / "tray_icon.png"
PFP_FOLDER = parent_folder() / "users/profile_pictures"

LOG = parent_folder().parent / "misc/logs.log"


def _copy(self: Path, target: Path) -> None:
    """Copy a given file to the given target destination.

    :param Path self: What to copy
    :param Path target: Where to copy self

    """
    import shutil

    assert self.is_file()
    shutil.copy(self, target)


# monkey Patch copy functionality into every Path instance
# noinspection PyTypeHints
Path.copy = _copy  # type: ignore


CREDENTIALS_SQL = """CREATE TABLE IF NOT EXISTS `credentials`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `profile_picture` varchar(255) NOT NULL DEFAULT 'default.png',
  `last_login_date` timestamp NULL DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `vault_existence` tinyint NOT NULL DEFAULT '0',
  `master_password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
         """

TOKENS_SQL = """CREATE TABLE IF NOT EXISTS `tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `token_UNIQUE` (`token`),
  KEY `id_idx` (`user_id`),
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `credentials` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
         """

VAULTS_SQL = """CREATE TABLE IF NOT EXISTS `vaults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `platform_name` varchar(255) NOT NULL,
  `website` varchar(512) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `vault_index` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  CONSTRAINT `id` FOREIGN KEY (`user_id`) REFERENCES `credentials` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

with database.database_manager() as db:
    db.execute(CREDENTIALS_SQL)
    db.execute(TOKENS_SQL)
    db.execute(VAULTS_SQL)
