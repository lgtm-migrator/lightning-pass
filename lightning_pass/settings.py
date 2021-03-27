"""Module with project constants and settings."""
from __future__ import annotations

import dotenv
import os
from pathlib import Path

from .util import database


def parent_folder() -> Path:
    """Return a Path to the parent folder of the settings script."""
    return Path(__file__).parent


def static_folder() -> Path:
    """Return a Path to the static folder located in the gui folder."""
    return parent_folder() / "gui/static"


dotenv.load_dotenv()
DB_DICT: dict = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_DB"),
}
EMAIL_DICT: dict = {
    "email": os.getenv("EMAIL_USER"),
    "password": os.getenv("EMAIL_PASS"),
}

LIGHT_STYLESHEET: Path = static_folder() / "light.qss"
DARK_STYLESHEET: Path = static_folder() / "dark.qss"

TRAY_ICON: Path = static_folder() / "tray_icon.png"
PFP_FOLDER: Path = parent_folder() / "users/profile_pictures"

LOG: Path = parent_folder().parent / "misc/logs.log"


def _copy(self: Path, target: Path) -> None:
    """Copy a given file to the given target destination.

    :param Path self: What to copy
    :param Path target: Where to copy self

    """
    import shutil

    assert self.is_file()
    shutil.copy(self, target)


# monkey Patch copy functionality into every pathlib.Path instance
# noinspection PyTypeHints
Path.copy = _copy  # type: ignore

with database.database_manager() as db:
    sql = """CREATE TABLE if not exists credentials(
            `id` int NOT NULL AUTO_INCREMENT,
            `username` varchar(255) NOT NULL,
            `password` varchar(255) NOT NULL,
            `email` varchar(255) NOT NULL,
            `profile_picture` varchar(255) NOT NULL DEFAULT 'default.png',
            `last_login_date` timestamp NULL DEFAULT NULL,
            `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
             PRIMARY KEY(`id`)
             )
             ENGINE = InnoDB
             AUTO_INCREMENT = 1
             DEFAULT CHARSET = utf8mb4
             COLLATE = utf8mb4_0900_ai_ci
             """
    db.execute(sql)

    sql = """CREATE TABLE if not exists tokens(
             `id` int NOT NULL AUTO_INCREMENT,
             `user_id` int NOT NULL,
             `token` varchar(255) NOT NULL,
             `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
             PRIMARY KEY (`id`)
             )
             ENGINE=InnoDB
             AUTO_INCREMENT = 1
             DEFAULT CHARSET=utf8mb4
             COLLATE=utf8mb4_0900_ai_ci
             """

    db.execute(sql)
