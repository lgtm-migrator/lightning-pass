"""Module containing the Buttons class.

Used for connecting each button on the GUI to various events or lambdas.

"""
import webbrowser
from typing import Callable, NamedTuple, Optional, Union

import clipboard
from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.util import regex


class Clickable(NamedTuple):
    """Store data on how to connect a clickable widget (``QPushButton`` or ``QAction``)."""

    widget: str
    event_type: str
    action: Union[str, Callable]


class VaultToolButton(NamedTuple):
    """Store information about connecting a ``QToolButton`` in the vault."""

    widget: str
    item: str
    source: str


class Buttons:
    """Used to setup buttons on the ``LightningPassWindow``."""

    __slots__ = "parent"

    def __init__(
        self,
        parent: QtWidgets.QMainWindow,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """Buttons constructor.

        :param parent: Main GUI window

        """
        super().__init__(*args, **kwargs)
        self.parent = parent

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.parent!r})"

    def setup_all(self):
        """Run all 3 funcs to setup everything."""
        self.setup_buttons()
        self.setup_menu_bar()
        self.data_validation()

    def setup_buttons(self) -> None:
        """Connect all buttons on all widgets"""
        buttons = (
            # home
            Clickable("home_login_btn", "home", "login"),
            Clickable("home_register_btn", "home", "register_2"),
            Clickable("home_generate_password_btn", "generator", "generate_pass"),
            # login
            Clickable("log_main_btn", "home", "home"),
            Clickable("log_forgot_pass_btn", "home", "forgot_password"),
            Clickable("log_login_btn_2", "home", "login_user"),
            # register
            Clickable("reg_main_btn", "home", "home"),
            Clickable("reg_register_btn", "home", "register_user"),
            # forgot_password
            Clickable("forgot_pass_main_menu_btn", "home", "home"),
            Clickable("forgot_pass_reset_btn", "home", "send_token"),
            # reset_token
            Clickable("reset_token_main_btn", "home", "home"),
            Clickable("reset_token_submit_btn", "home", "submit_reset_token"),
            # reset_password
            Clickable("reset_password_confirm_btn", "home", "reset_password_submit"),
            Clickable("reset_password_main_btn", "home", "home"),
            # change_password
            Clickable("change_password_main_btn", "home", "home"),
            Clickable(
                "change_password_confirm_btn",
                "account",
                "submit_change_password",
            ),
            # generate_pass
            Clickable(
                "generate_pass_generate_btn",
                "generator",
                "generate_pass_phase2",
            ),
            Clickable("generate_pass_main_menu_btn", "home", "home"),
            # generate_pass_phase2
            Clickable("generate_pass_p2_main_btn", "home", "home"),
            Clickable("generate_pass_p2_reset_btn", "generator", "generate_pass_again"),
            # account
            Clickable("account_main_menu_btn", "home", "home"),
            Clickable("account_change_pfp_btn", "account", "change_pfp"),
            Clickable("account_logout_btn", "account", "logout"),
            Clickable("account_change_pass_btn", "account", "change_password"),
            Clickable("account_edit_details_btn", "account", "edit_details"),
            Clickable("account_vault_btn", "vault", "vault"),
            # vault
            Clickable("vault_add_page_btn", "vault", "add_vault_page"),
            Clickable("vault_remove_page_btn", "vault", "remove_vault_page"),
            Clickable("vault_menu_btn", "home", "home"),
            Clickable("vault_lock_btn", "vault", "lock_vault"),
            # master_password
            Clickable("master_pass_menu_btn", "home", "home"),
            Clickable("master_pass_save_btn", "account", "master_password_submit"),
        )

        for button in buttons:
            getattr(self.parent.ui, button.widget).clicked.connect(
                getattr(getattr(self.parent.events, button.event_type), button.action),
            )

        # miscellaneous
        self.parent.ui.generate_pass_p2_copy_tool_btn.clicked.connect(
            lambda: clipboard.copy(
                self.parent.ui.generate_pass_p2_final_pass_line.text(),
            ),
        )

    def setup_menu_bar(self) -> None:
        """Connect all menu bar actions."""
        menu_bar = (
            # menu_general
            Clickable("action_main_menu", "home", "home"),
            # menu_password
            Clickable("action_generate", "generator", "generate_pass"),
            # menu_users
            Clickable("action_login", "home", "login"),
            Clickable("action_register", "home", "register_2"),
            Clickable("action_forgot_password", "home", "forgot_password"),
            Clickable("action_reset_token", "home", "reset_token"),
            # menu_account
            Clickable("action_profile", "account", "account"),
            Clickable("action_change_password", "account", "change_password"),
            Clickable("action_vault", "vault", "vault"),
            Clickable("action_master_password", "account", "master_password"),
        )

        for button in menu_bar:
            getattr(self.parent.ui, button.widget).triggered.connect(
                getattr(getattr(self.parent.events, button.event_type), button.action),
            )

        self.parent.ui.action_light.triggered.connect(
            lambda: self.parent.main_win.setStyleSheet(self.parent.light_stylesheet),
        )
        self.parent.ui.action_dark.triggered.connect(
            lambda: self.parent.main_win.setStyleSheet(self.parent.dark_stylesheet),
        )

    def data_validation(self) -> None:
        """Disable whitespaces in some input fields."""
        lines_to_validate = {
            "reg_username_line",
            "reg_password_line",
            "reg_conf_pass_line",
            "reg_email_line",
            "reset_password_new_pass_line",
            "reset_password_conf_new_pass_line",
            "change_password_new_pass_line",
            "change_password_conf_new_line",
            "account_username_line",
            "account_email_line",
            "master_pass_master_pass_line",
            "master_pass_conf_master_pass_line",
        }

        for line in lines_to_validate:
            getattr(self.parent.ui, line).setValidator(
                QtGui.QRegExpValidator(QtCore.QRegExp(regex.NON_WHITESPACE.pattern)),
            )

    def setup_vault_buttons(self):
        """Connect all buttons on a new vault widget."""

        # tool buttons for copying vault items
        vault_copy_tool_buttons = (
            VaultToolButton(
                "vault_copy_username_tool_btn",
                "username",
                "vault_username_line",
            ),
            VaultToolButton("vault_copy_email_tool_btn", "email", "vault_email_line"),
            VaultToolButton(
                "vault_copy_password_tool_btn",
                "password",
                "vault_password_line",
            ),
        )

        parent = self.parent.ui.vault_widget_instance.ui
        events = self.parent.events

        parent.vault_open_web_tool_btn.clicked.connect(
            lambda: _open_website(parent.vault_web_line.text()),
        )
        for button in vault_copy_tool_buttons:
            getattr(parent, button.widget).clicked.connect(
                # since lambda has a default > dump the first bool passed in by the widget parent
                lambda _, line=getattr(parent, button.source): _copy_text(line),
            )

        parent.vault_update_btn.clicked.connect(
            events.vault.update_vault_page,
        )

        parent.vault_forward_tool_btn.clicked.connect(
            lambda: events.vault.change_vault_page(1, calculate=True),
        )
        parent.vault_backward_tool_btn.clicked.connect(
            lambda: events.vault.change_vault_page(-1, calculate=True),
        )


def _copy_text(obj: QtWidgets.QLineEdit):
    """Copy a text into clipboard.

    :param obj: The source of the text to copy

    """
    clipboard.copy(obj.text())


def _open_website(url: Optional[str]) -> None:
    """Open a website in the default browser.

    :param url: The URL to open

    """
    if url:
        webbrowser.get().open(url, new=2)


__all__ = [
    "Buttons",
    "Clickable",
    "VaultToolButton",
]
